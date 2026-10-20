#!/bin/bash
# tis-login.sh - Headless login for techinfo.toyota.com with MFA support
#
# Authenticates against Toyota's OpenAM identity provider using its REST API,
# handles MFA (email or SMS OTP), then saves session cookies into cookies.txt
# for use by the tis-clone download scripts.
#
# Usage:
#   ./tis-login.sh                         (prompts for all input interactively)
#   ./tis-login.sh -u USERNAME             (prompts for password and MFA)
#   ./tis-login.sh -u USERNAME -p PASSWORD (prompts for MFA choice and OTP only)
#   ./tis-login.sh -m 0                    (pre-select MFA: 0=email, 1=SMS)
#
# Defaults can also be set in ~/.tis/tis-clone.cfg with TIS_USERNAME,
# TIS_PASSWORD and TIS_MFA.  Command line options override them.
#
# Requirements: curl, python3

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

OPENAM_AUTH_URL="https://ep.fram.idm.toyota.com/openam/json/realms/root/realms/dealerdaily/authenticate?authIndexType=service&authIndexValue=Techinfo"
TIS_PORTAL_URL="$WEBSITE/t3Portal/login"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COOKIE_FILE=$COOKIES
#COOKIE_FILE="$HOME/.cookies.txt"
export TMP_DIR
TMP_DIR=$(mktemp -d /tmp/tis-login.XXXXXX)
TMP_COOKIE="$TMP_DIR/cookies.txt"

[ -d "$TMP_DIR" ] || { echo "ERROR: Failed to create temp directory"; exit 1; }

USER_AGENT="Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"

cleanup() {
    rm -rf "$TMP_DIR"
    #echo "See $TMP_DIR"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Helper: die with a message
# ---------------------------------------------------------------------------

die() {
    echo "ERROR: $*" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Helper: POST JSON to OpenAM, save response to a named temp file, return it
# ---------------------------------------------------------------------------

openam_post() {
    local infile="$1"   # file containing JSON payload (use /dev/null for empty POST)
    local outfile="$2"
    curl -s \
        -X POST "$OPENAM_AUTH_URL" \
        -H "Content-Type: application/json" \
        -H "Accept-API-Version: resource=2.1" \
        -H "User-Agent: $USER_AGENT" \
        -c "$TMP_COOKIE" -b "$TMP_COOKIE" \
        --data-binary "@$infile" \
        -o "$outfile"
}

# Touch the cookie file so curl -b doesn't complain about missing file
touch "$TMP_COOKIE"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

USERNAME="${TIS_USERNAME:-}"
PASSWORD="${TIS_PASSWORD:-}"
MFA_CHOICE="${TIS_MFA:-}"

while getopts "u:p:m:" opt; do
    case $opt in
        u) USERNAME="$OPTARG" ;;
        p) PASSWORD="$OPTARG" ;;
        m) MFA_CHOICE="$OPTARG" ;;
        *) echo "Usage: $0 [-u username] [-p password] [-m 0|1]"; exit 1 ;;
    esac
done

if [ -z "$USERNAME" ]; then
    read -rp "TIS Username: " USERNAME
fi
if [ -z "$PASSWORD" ]; then
    read -rsp "TIS Password: " PASSWORD
    echo
fi

# ---------------------------------------------------------------------------
# Step 1: Get initial challenge
# ---------------------------------------------------------------------------

echo "[1/5] Requesting authentication challenge..."

echo '{}' > "$TMP_DIR/empty.json"
openam_post "$TMP_DIR/empty.json" "$TMP_DIR/challenge.json"

python3 - << 'PYEOF' || die "Unexpected response from OpenAM. See $TMP_DIR/challenge.json"
import json, os, sys
with open(os.environ['TMP_DIR'] + '/challenge.json') as f:
    data = json.load(f)
if 'authId' not in data or 'callbacks' not in data:
    print(json.dumps(data), file=sys.stderr)
    sys.exit(1)
PYEOF

echo "    Challenge received."

# ---------------------------------------------------------------------------
# Step 2: Inject credentials and submit
# ---------------------------------------------------------------------------

echo "[2/5] Submitting credentials..."

export TIS_USER="$USERNAME"
export TIS_PASS="$PASSWORD"

python3 - << 'PYEOF' > "$TMP_DIR/cred_payload.json" || die "Failed to build credential payload"
import json, os
with open(os.environ['TMP_DIR'] + '/challenge.json') as f:
    data = json.load(f)
for cb in data['callbacks']:
    if cb.get('type') == 'NameCallback':
        cb['input'][0]['value'] = os.environ['TIS_USER']
    elif cb.get('type') == 'PasswordCallback':
        cb['input'][0]['value'] = os.environ['TIS_PASS']
print(json.dumps(data))
PYEOF

openam_post "$TMP_DIR/cred_payload.json" "$TMP_DIR/mfa_response.json"

# ---------------------------------------------------------------------------
# Step 3: Handle MFA ChoiceCallback
# ---------------------------------------------------------------------------

MFA_TYPE=$(python3 -c "
import json, sys
with open('$TMP_DIR/mfa_response.json') as f:
    data = json.load(f)
cbs = data.get('callbacks', [])
print(cbs[0].get('type','') if cbs else '')
")

if [ "$MFA_TYPE" = "ChoiceCallback" ]; then

    echo "[3/5] MFA required. Choose a verification method:"

    python3 - << 'PYEOF'
import json, os
with open(os.environ['TMP_DIR'] + '/mfa_response.json') as f:
    data = json.load(f)
choices = data['callbacks'][0]['output'][1]['value']
for i, choice in enumerate(choices):
    print(f"  {i}) {choice}")
PYEOF

    if [ -z "$MFA_CHOICE" ]; then
        read -rp "Enter choice number: " MFA_CHOICE
    else
        echo "    Using pre-selected method: $MFA_CHOICE"
    fi
    export MFA_CHOICE

    python3 - << 'PYEOF' > "$TMP_DIR/choice_payload.json" || die "Failed to build MFA choice payload"
import json, os
with open(os.environ['TMP_DIR'] + '/mfa_response.json') as f:
    data = json.load(f)
data['callbacks'][0]['input'][0]['value'] = int(os.environ['MFA_CHOICE'])
print(json.dumps(data))
PYEOF

    openam_post "$TMP_DIR/choice_payload.json" "$TMP_DIR/otp_challenge.json"
    echo "    Verification code sent."

else
    # No choice step — copy mfa_response as the otp challenge
    cp "$TMP_DIR/mfa_response.json" "$TMP_DIR/otp_challenge.json"
fi

# ---------------------------------------------------------------------------
# Step 4: Submit OTP if required
# ---------------------------------------------------------------------------

OTP_TYPE=$(python3 -c "
import json
with open('$TMP_DIR/otp_challenge.json') as f:
    data = json.load(f)
if 'tokenId' in data:
    print('tokenId')
elif data.get('callbacks'):
    print(data['callbacks'][0].get('type','unknown'))
else:
    print('unknown')
")

if [ "$OTP_TYPE" != "tokenId" ]; then

    echo "[4/5] Enter the verification code sent to you:"
    read -rp "OTP code: " OTP_CODE
    export OTP_CODE

    python3 - << 'PYEOF' > "$TMP_DIR/otp_payload.json" || die "Failed to build OTP payload"
import json, os
with open(os.environ['TMP_DIR'] + '/otp_challenge.json') as f:
    data = json.load(f)
data['callbacks'][0]['input'][0]['value'] = os.environ['OTP_CODE']
print(json.dumps(data))
PYEOF

    openam_post "$TMP_DIR/otp_payload.json" "$TMP_DIR/token_response.json"

else
    cp "$TMP_DIR/otp_challenge.json" "$TMP_DIR/token_response.json"
fi

# ---------------------------------------------------------------------------
# Step 5: Extract tokenId and establish portal session
# ---------------------------------------------------------------------------

echo "[5/5] Extracting session token and establishing portal session..."

TOKEN_ID=$(python3 - << 'PYEOF'
import json, os, sys
with open(os.environ['TMP_DIR'] + '/token_response.json') as f:
    data = json.load(f)
if 'tokenId' not in data:
    print('tokenId not found. Server response: ' + json.dumps(data), file=sys.stderr)
    sys.exit(1)
print(data['tokenId'])
PYEOF
)

if [ -z "$TOKEN_ID" ]; then
    die "Authentication failed — no token received. Check your OTP code, username, and password."
fi

echo "    Token obtained: ${TOKEN_ID:0:24}... (truncated)"

# Write the OpenAM token into the cookie jar so curl sends it properly
# Netscape cookie format: domain  flag  path  secure  expiry  name  value
printf "ep.fram.idm.toyota.com\tTRUE\t/\tTRUE\t2147483647\tiPlanetDirectoryPro\t%s\n" "$TOKEN_ID" >> "$TMP_COOKIE"
printf "techinfo.toyota.com\tTRUE\t/\tTRUE\t2147483647\tiPlanetDirectoryPro\t%s\n" "$TOKEN_ID" >> "$TMP_COOKIE"

# Use the OpenAM token to get TIS portal session cookies
curl -s -o "$TMP_DIR/portal.html" -w "%{http_code}\n" \
    -L \
    -A "$USER_AGENT" \
    -c "$TMP_COOKIE" -b "$TMP_COOKIE" \
    -H "Referer: https://techinfo.toyota.com/" \
    "$TIS_PORTAL_URL" > "$TMP_DIR/http_status.txt"

HTTP_STATUS=$(cat "$TMP_DIR/http_status.txt")

# Debug: show what cookies were collected
echo "    Cookies collected:"
grep -v '^#' "$TMP_COOKIE" | awk '{print "      " $6}' || echo "      (none)"

SESSION_COOKIE=$(grep -i "T3SESSIONID" "$TMP_COOKIE" 2>/dev/null || true)

if [ -z "$SESSION_COOKIE" ]; then
    echo ""
    echo "ERROR: No T3SESSIONID cookie received. HTTP status: $HTTP_STATUS"
    [ "$HTTP_STATUS" = "000" ] && echo "       Could not connect to TIS (000).  The portal may be down or overloaded; try again later."
    if [ -s "$TMP_DIR/portal.html" ]; then
        echo "       Portal page snippet:"
        head -20 "$TMP_DIR/portal.html" | sed 's/^/         /'
    fi
    exit 1
fi

# The portal landing page is not a reliable sign of success (TIS sometimes answers it with a 403 even
# though the session works), so fetch a subscriber-only PDF with the new cookies, as confirm-login.sh
# does.  Try a few times since the portal can be slow or drop connections.
TESTPAGE="/t3Portal/staticcontent/en/techinfo/docs/glossary.pdf"
for TRY in 1 2 3; do
    curl -s -o "$TMP_DIR/test.pdf" -m 60 -A "$USER_AGENT" -b "$TMP_COOKIE" "$WEBSITE$TESTPAGE"
    [ "$(head -c 4 "$TMP_DIR/test.pdf" 2>/dev/null)" = "%PDF" ] && break
    rm -f "$TMP_DIR/test.pdf"
    [ $TRY = 3 ] || sleep 10
done

if [ -f "$TMP_DIR/test.pdf" ]; then
    cp "$TMP_COOKIE" "$COOKIE_FILE"
    echo ""
    echo "Login successful! Cookies saved to: $COOKIE_FILE"
    [ "$HTTP_STATUS" = "200" ] || echo "         (The portal page answered HTTP $HTTP_STATUS, but the session works.)"
else
    # Keep the page TIS returned so we can see why (concurrent login, account locked, outage, ...)
    cp "$TMP_DIR/portal.html" "$(dirname "$COOKIE_FILE")/last-login-portal.html" 2>/dev/null
    echo ""
    echo "ERROR: Got a session cookie, but it could not fetch the test page $TESTPAGE."
    echo "       Cookies NOT saved.  Portal page HTTP status: $HTTP_STATUS, saved to $(dirname "$COOKIE_FILE")/last-login-portal.html"
    echo "       Title: $(grep -io '<title>[^<]*' "$TMP_DIR/portal.html" 2>/dev/null | head -1 | sed 's/<title>//I')"
    exit 1
fi
