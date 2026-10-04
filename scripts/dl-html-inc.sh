#!/bin/sh
#
# Download Body Repair Manualdocs
#

. ${HOME}/.tis/tis-clone.cfg
${SCRIPT_BASE}/confirm-login.sh || exit 1

if [ x$1 = x ]; then
	echo "Syntax: $0 [WEBSITE URI PATH]"
	echo "    ie: $0 /t3Portal/external/en/bm/BM27J0U"
	exit
fi

FOLDER=$1

##
## Get Repair Manual 
##

# A rejected session redirects to concurrentLoginFailure.html (issue #11) or to the login page,
# and wget saves that page in place of each document.  Check every fetch and stop instead.
rejected() {
	if grep -qE 'concurrentLoginFailure|techInfoPortal/login' $1; then
		echo "TIS rejected the session at $2: it expired, or the account is logged in elsewhere.  Stopping."
		echo "Log out of TIS in any browser, run ${SCRIPT_BASE}/tis-login.sh, then rerun this script."
		exit 1
	fi
}

## TOC
$WG ${WEBSITE}/${FOLDER}/toc.xml > ${TISTMPDIR}/dl-html-inc.last 2>&1
cat ${TISTMPDIR}/dl-html-inc.last >> ${TISTMPDIR}/dl-html-inc.log
rejected ${TISTMPDIR}/dl-html-inc.last ${FOLDER}/toc.xml
if ! grep -q "href=.*xhtml" ${FSM_URLBASE}/${FOLDER}/toc.xml 2>/dev/null; then
	echo "No documents in ${FOLDER}/toc.xml.  Is the identifier right for this manual type?"
	exit 1
fi

## HTML Docs and Images/PDFs
for DOC in `grep "href=.*xhtml" ${FSM_URLBASE}/${FOLDER}/toc.xml |cut -d\" -f2`; do
	URL=`echo ${DOC} | sed -e 's/$/\?sisuffix=ff\&locale=en\&siid='"${SIID}"'/g'`;
	echo "${DOC}"
	$WG "${WEBSITE}/${URL}" > ${TISTMPDIR}/dl-html-inc.last 2>&1
	cat ${TISTMPDIR}/dl-html-inc.last >> ${TISTMPDIR}/dl-html-inc.log
	rejected ${TISTMPDIR}/dl-html-inc.last ${DOC}
	mv -f ${FSM_URLBASE}/${URL} ${FSM_URLBASE}/${DOC}
done

# Create JSP static navigation
if [ -f ${FSM_URLBASE}/${FOLDER}/toc.xml ]; then
	${SCRIPT_BASE}/toc2html ${FSM_URLBASE}/${FOLDER}/toc.xml > ${FSM_URLBASE}/${FOLDER}/toc.html
	cp ${BASE}/website-framework/index.html  ${FSM_URLBASE}/${FOLDER}/
fi

