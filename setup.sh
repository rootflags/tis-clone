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

# ---- Dependencies -------------------------------------------------------------------------------
# Everything is checked before anything is said, then the missing pieces are listed with the command that
# installs them on this system (apt, dnf, pacman, zypper or Homebrew), which we offer to run.

PM=""
for P in apt-get dnf pacman zypper brew; do
	if which ${P} > /dev/null 2>&1; then PM=${P}; break; fi
done

# pkg NAME: this system's package for NAME (a command, or py-MODULE for a Python module)
pkg() {
	case "${PM}:$1" in
		*:xargs|*:find) echo findutils ;;
		*:cut|*:head|*:sort|*:tr|*:cat|*:mkdir|*:mv|*:rm|*:cp|*:ls) echo coreutils ;;
		*:awk) echo gawk ;;
		*:gs) echo ghostscript ;;
		pacman:python3|brew:python3) echo python ;;
		pacman:py-*) echo python-${1#py-} ;;
		brew:py-*) echo "" ;;                         # pip3 install, below
		*:py-*) echo python3-${1#py-} ;;
		apt-get:pdfinfo|apt-get:pdfseparate|dnf:pdfinfo|dnf:pdfseparate) echo poppler-utils ;;
		zypper:pdfinfo|zypper:pdfseparate) echo poppler-tools ;;
		*:pdfinfo|*:pdfseparate) echo poppler ;;
		apt-get:pdftk|dnf:pdftk|brew:pdftk) echo pdftk-java ;;
		*:wkhtmltopdf) echo "" ;;                       # needs the "patched qt" build, below
		*) echo $1 ;;
	esac
}

check() {
	MISSING_REQ=""; MISSING_PDF=""; MISSING_OPT=""
	for C in bash curl python3 gzip xargs find grep sed awk cut head sort tr; do
		which ${C} > /dev/null 2>&1 || MISSING_REQ="${MISSING_REQ} ${C}"
	done
	if which python3 > /dev/null 2>&1; then
		python3 -c "import requests" > /dev/null 2>&1 || MISSING_REQ="${MISSING_REQ} py-requests"
		python3 -c "import pikepdf" > /dev/null 2>&1 || MISSING_PDF="${MISSING_PDF} py-pikepdf"
	fi
	for C in gs wkhtmltopdf; do
		which ${C} > /dev/null 2>&1 || MISSING_PDF="${MISSING_PDF} ${C}"
	done
	for C in pdfinfo pdfseparate pdftk rsync; do
		which ${C} > /dev/null 2>&1 || MISSING_OPT="${MISSING_OPT} ${C}"
	done
}

# Names for people: py-requests -> Python module requests
names() {
	for N in "$@"; do
		case ${N} in py-*) printf '%s ' "Python module ${N#py-}," ;; *) printf '%s ' "${N}," ;; esac
	done | sed -e 's/, $//'
}

report() {
	[ -n "${MISSING_REQ}" ] && echo "** Missing, needed to download: `names ${MISSING_REQ}`"
	[ -n "${MISSING_PDF}" ] && echo "** Missing, needed to make PDFs (or run tis-clone with --no-pdf): `names ${MISSING_PDF}`"
	[ -n "${MISSING_OPT}" ] && echo "   Missing, optional (repdf needs pdfinfo, pdfseparate and pdftk; tis-merge.sh needs rsync): `names ${MISSING_OPT}`"
	PKGS=""; PIPS=""
	for N in ${MISSING_REQ} ${MISSING_PDF} ${MISSING_OPT}; do
		P=`pkg ${N}`
		if [ -n "${P}" ]; then
			case " ${PKGS} " in *" ${P} "*) ;; *) PKGS="${PKGS} ${P}" ;; esac
		elif [ "${PM}" = brew ] && [ "${N#py-}" != "${N}" ]; then
			PIPS="${PIPS} ${N#py-}"
		fi
	done
	SUDO=""
	[ `id -u` != 0 ] && [ "${PM}" != brew ] && SUDO="sudo "
	case "${PM}" in
		apt-get) INSTALL="${SUDO}apt-get install -y" ;;
		dnf) INSTALL="${SUDO}dnf install -y" ;;
		pacman) INSTALL="${SUDO}pacman -S --needed" ;;
		zypper) INSTALL="${SUDO}zypper install -y" ;;
		brew) INSTALL="brew install" ;;
		*) INSTALL="" ;;
	esac
	if [ -n "${PKGS}" ]; then
		if [ -n "${INSTALL}" ]; then
			echo "   To install them: ${INSTALL}${PKGS}"
		else
			echo "   Install these with your system's package manager:${PKGS}"
		fi
	fi
	[ -n "${PIPS}" ] && echo "   And the Python modules: pip3 install${PIPS}"
	case " ${MISSING_PDF} " in *" wkhtmltopdf "*)
		echo "   wkhtmltopdf: get the \"with patched qt\" build from https://wkhtmltopdf.org/downloads.html (distributions'"
		echo "   own packages lack it, and the links inside the PDFs need it)" ;;
	esac
}

echo "Checking dependencies..."
check
if [ -n "${MISSING_REQ}${MISSING_PDF}${MISSING_OPT}" ]; then
	report
	if [ -t 0 ] && [ -n "${INSTALL}" ] && [ -n "${PKGS}${PIPS}" ]; then
		printf 'Install them now? [y/N] '
		read -r ANSWER || ANSWER=n
		case "${ANSWER}" in
			[yY]*)
				[ "${PM}" = apt-get ] && ${SUDO}apt-get update
				[ -n "${PKGS}" ] && ${INSTALL}${PKGS}
				[ -n "${PIPS}" ] && pip3 install${PIPS}
				echo "Checking again..."
				check
				[ -n "${MISSING_REQ}${MISSING_PDF}${MISSING_OPT}" ] && report ;;
		esac
	fi
	if [ -n "${MISSING_REQ}" ]; then
		echo "** tis-clone can't download until the missing pieces above are installed.  Run $0 again afterwards."
		exit 1
	fi
fi
if which wkhtmltopdf > /dev/null 2>&1 && ! wkhtmltopdf -V 2>/dev/null | grep -q "patched qt"; then
	echo "** Warning: wkhtmltopdf is not the \"with patched qt\" build, so links inside PDFs won't work."
	echo "   Get it from https://wkhtmltopdf.org/downloads.html"
fi

echo "Creating folders..."
mkdir -p "${TISTMPDIR}" || exit 1
mkdir -p "${DOWNLOAD_TO}" || exit 1

echo
echo "Setup is done.  Next, log in to TIS and download, ie:"
echo "    ${SCRIPT_BASE}/tis-login.sh"
echo "    ${BASE}/tis-clone          (it asks for the make, model and year)"
