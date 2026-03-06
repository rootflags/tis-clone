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
# Requirements: curl, python3

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
#

. ${HOME}/.tis/tis-clone.cfg

OPENAM_AUTH_URL="https://ep.fram.idm.toyota.com/openam/json/realms/root/realms/dealerdaily/authenticate?authIndexType=service&authIndexValue=Techinfo"
TIS_PORTAL_URL="$WEBSITE/t3Portal/login"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_COOKIE="$TISTMPDIR/cookies.txt"

USER_AGENT="Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"

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
    local payload="$1"
    local outfile="$2"
    curl -s \
        -X POST "$OPENAM_AUTH_URL" \
        -H "Content-Type: application/json" \
        -H "Accept-API-Version: resource=2.1" \
        -H "User-Agent: $USER_AGENT" \
        -c "$TMP_COOKIE" -b "$TMP_COOKIE" \
        -d "$payload" \
        -o "$outfile"
}

# Touch the cookie file so curl -b doesn't complain about missing file
touch "$TMP_COOKIE"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

USERNAME=""
PASSWORD=""
MFA_CHOICE=""

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

openam_post '{}' "$TMP_DIR/challenge.json"

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

openam_post "$(cat "$TMP_DIR/cred_payload.json")" "$TMP_DIR/mfa_response.json"

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

    openam_post "$(cat "$TMP_DIR/choice_payload.json")" "$TMP_DIR/otp_challenge.json"
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

    openam_post "$(cat "$TMP_DIR/otp_payload.json")" "$TMP_DIR/token_response.json"

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

# Use the OpenAM token to get TIS portal session cookies
curl -s -o "$TMP_DIR/portal.html" -w "%{http_code}\n" \
    -L \
    -A "$USER_AGENT" \
    -c "$TMP_COOKIE" \
    -b "$TMP_COOKIE;iPlanetDirectoryPro=$TOKEN_ID" \
    -H "Referer: https://techinfo.toyota.com/" \
    "$TIS_PORTAL_URL" > "$TMP_DIR/http_status.txt"

HTTP_STATUS=$(cat "$TMP_DIR/http_status.txt")

# Debug: show what cookies were collected
echo "    Cookies collected:"
grep -v '^#' "$TMP_COOKIE" | awk '{print "      " $6}' || echo "      (none)"

SESSION_COOKIE=$(grep -i "TISESSIONID" "$TMP_COOKIE" 2>/dev/null || true)
SIGNOUT_LINK=$(grep -i "tessSignoff\|logout\|signout" "$TMP_DIR/portal.html" 2>/dev/null || true)

if [ -n "$SESSION_COOKIE" ] && [ -n "$SIGNOUT_LINK" ]; then
    cp "$TMP_COOKIE" "$COOKIES"
    echo ""
    echo "Login successful! Cookies saved to: $COOKIES"
elif [ -n "$SESSION_COOKIE" ]; then
    cp "$TMP_COOKIE" "$COOKIES"
    echo ""
    echo "WARNING: Session cookie set but sign-out link not detected in page."
    echo "         Cookies saved to: $COOKIES"
    echo "         If downloads fail, check credentials and try again."
else
    echo ""
    echo "ERROR: No TISESSIONID cookie received. HTTP status: $HTTP_STATUS"
    echo "       Portal page snippet:"
    head -20 "$TMP_DIR/portal.html" | sed 's/^/         /'
    exit 1
fi
