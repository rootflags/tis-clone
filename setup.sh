#!/bin/sh
#
# Initial setup script
#
# Creates ~/.tis/tis-clone.cfg from the repo's tis-clone.cfg if you don't have one yet, then walks you
# through the settings you're likely to change (download folder, TIS login).  Run it again any time to
# review them; Enter keeps the current value.  Then it checks the software tis-clone needs and creates
# the folders.
#
# Without a terminal (ie: from a script) it doesn't ask anything, and only creates the config and folders.
#

FOLDER=`cd \`dirname $0\` && pwd`
CONFIG_DIR=${HOME}/.tis
CFG=${CONFIG_DIR}/tis-clone.cfg
STOCK_SIID=1520435234586

# set_var NAME VALUE: set NAME='VALUE' in $CFG, replacing its first NAME= or #NAME= line (or adding one).
# Clearing a setting that's only there as a commented-out example leaves the example alone.
set_var() {
	[ x"$2" = x ] && ! grep -q "^$1=" "${CFG}" && return
	Q=$(printf '%s' "$2" | sed "s/'/'\\\\''/g")
	SET_LINE="$1='$Q'" SET_NAME="$1" awk '
		!done && $0 ~ ("^#?" ENVIRON["SET_NAME"] "=") { print ENVIRON["SET_LINE"]; done = 1; next }
		{ print }
		END { if (!done) print ENVIRON["SET_LINE"] }' "${CFG}" > "${CFG}.new" && cat "${CFG}.new" > "${CFG}"
	rm -f "${CFG}.new"
}

# ask NAME QUESTION [hidden]: show NAME's current value and read a new one into ANSWER.  Enter keeps the
# current value, "-" clears it.  Returns 1 if the value didn't change.
ask() {
	eval "CUR=\${$1}"
	SHOW="${CUR}"
	[ x"$3" = xhidden ] && [ x"${CUR}" != x ] && SHOW="(set)"
	printf '%s\n    [%s]: ' "$2" "${SHOW}"
	[ x"$3" = xhidden ] && stty -echo
	read -r ANSWER || ANSWER=
	[ x"$3" = xhidden ] && { stty echo; echo; }
	case "${ANSWER}" in
		"") ANSWER="${CUR}" ;;
		-) ANSWER="" ;;
		"~") ANSWER="${HOME}" ;;
		"~/"*) ANSWER="${HOME}/${ANSWER#\~/}" ;;
	esac
	[ x"${ANSWER}" != x"${CUR}" ]
}

if [ -f ${CFG} ]; then
	echo "Using your settings in ${CFG}"
	NEW=0
else
	echo "Creating ${CFG} from ${FOLDER}/tis-clone.cfg"
	mkdir -p ${CONFIG_DIR}
	# Private, since it can hold your TIS password
	( umask 077; cp ${FOLDER}/tis-clone.cfg ${CFG} )
	NEW=1
fi
. ${CFG}

# Give this install its own siid (see SIID in tis-clone.cfg and issue #11)
if [ x"${SIID}" = x ] || [ x"${SIID}" = x${STOCK_SIID} ]; then
	set_var SIID 1`LC_ALL=C tr -dc 0-9 < /dev/urandom 2>/dev/null | head -c 12`
fi

# The scripts find each other through BASE, so it must be where this copy of tis-clone is
if [ ! -f "${SCRIPT_BASE}/tis-fetch.py" ] || [ "`cd ${BASE} 2>/dev/null && pwd`" != "${FOLDER}" ]; then
	echo "Setting BASE to ${FOLDER}, where tis-clone is installed (it was ${BASE})"
	set_var BASE "${FOLDER}"
fi

if [ -t 0 ]; then
	REVIEW=y
	if [ ${NEW} = 0 ]; then
		printf 'Review your settings now? [y/N] '
		read -r REVIEW || REVIEW=n
	fi
	case "${REVIEW}" in
	[yY]*)
		# Ctrl-C at the password prompt mustn't leave the terminal not showing what you type
		trap 'stty echo; echo; exit 130' INT
		. ${CFG}
		echo
		echo "Press Enter to keep the value in [brackets], or type a new one (\"-\" clears it)."
		echo

		ask DOWNLOAD_TO "Where should downloads go?  Use a separate folder for each vehicle, ie: ~/tis-download-rav4" &&
			set_var DOWNLOAD_TO "${ANSWER}"

		echo
		echo "Your TIS login.  Saving it here means tis-login.sh (and a download whose session expires) only"
		echo "asks for the 2FA code.  Leave it empty to type it each time."
		ask TIS_USERNAME "TIS username (email address)" && set_var TIS_USERNAME "${ANSWER}"
		ask TIS_PASSWORD "TIS password (not shown as you type)" hidden && set_var TIS_PASSWORD "${ANSWER}"
		while ask TIS_MFA "Send the 2FA code by 0 = email or 1 = text message"; do
			case "${ANSWER}" in
				""|0|1) set_var TIS_MFA "${ANSWER}"; break ;;
			esac
			echo "    Please answer 0 or 1"
		done
		trap - INT

		echo
		echo "If you publish your download on a website, its address.  Links in a PDF to another manual"
		echo "(ie: from the repair manual to a wiring diagram) go there; with http://localhost they're left out."
		while ask MYURL "Your website's address, ie: https://fsm.example.com"; do
			case "${ANSWER}" in
				""|http://*|https://*) set_var MYURL "${ANSWER%/}"; break ;;
			esac
			echo "    Please give an address starting with http:// or https://"
		done
		ask MYURL_BASE "The folder your web server serves that website from (only the older tis-pdfer.sh, tis-html2pdf2.sh and tis-xhtml2pdf.sh use it)" &&
			set_var MYURL_BASE "${ANSWER}"
		echo
		echo "Saved.  The other settings are described in ${CFG}"
		;;
	esac
elif [ ${NEW} = 1 ]; then
	echo "** Check the settings in ${CFG} (at least DOWNLOAD_TO), or run $0 in a terminal to be asked"
fi
. ${CFG}

# A password in the config must stay private
if [ x"${TIS_PASSWORD}" != x ] && [ x"`ls -l ${CFG} | cut -c5-10`" != x------ ]; then
	echo "Making ${CFG} private, since it holds your TIS password"
	chmod 600 ${CFG}
fi

echo "Checking dependencies..."
# Confirm we have all the basic packages required
for cmd in bash cat cp curl cut diff find grep gzip head ls mkdir mv python3 rm rmdir sed sort xargs gs pdfinfo pdfseparate pdftk rsync wkhtmltopdf; do
	which $cmd > /dev/null 2>&1
	if [ $? != 0 ]; then
		echo "** $cmd not found"
		exit 1
	fi
done

# The downloader, tis-fetch.py, needs the Python requests module
python3 -c "import requests" > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "** Python module requests not found (apt install python3-requests)"
	exit 1
fi

# PDFs: tis-pdfbook.py needs pikepdf, and wkhtmltopdf's "patched qt" build for links inside the PDFs
python3 -c "import pikepdf" > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "** Python module pikepdf not found (apt install python3-pikepdf).  Needed to make PDFs."
	exit 1
fi
wkhtmltopdf -V 2>/dev/null | grep -q "patched qt"
if [ $? != 0 ]; then
	echo "** Warning: wkhtmltopdf is not the \"with patched qt\" build, so links inside PDFs won't work."
	echo "   Get it from https://wkhtmltopdf.org/downloads.html"
fi

echo "Creating folders..."
mkdir -p "${TISTMPDIR}" || exit 1
mkdir -p "${DOWNLOAD_TO}" || exit 1

echo
echo "Setup is done.  Next, log in to TIS and download, ie:"
echo "    ${SCRIPT_BASE}/tis-login.sh"
echo "    ${BASE}/tis-clone 30B0U"
