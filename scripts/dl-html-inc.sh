#!/bin/sh
#
# Download an HTML manual (repair, body/collision, new car features) listed in a toc.xml
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 [WEBSITE URI PATH]"
	echo "    ie: $0 /t3Portal/external/en/cr/BM27J0U"
	exit
fi

FOLDER=$1

# tis-fetch.py checks every response for an expired session, logs in again when it happens (you'll
# be asked for the 2FA code) and records progress in $DOWNLOAD_TO/MANIFEST, so rerunning this
# script after a failure picks up where it stopped.  Exit status 75 means the session expired and
# could not be renewed.

## TOC
${SCRIPT_BASE}/tis-fetch.py "${FOLDER}/toc.xml" || exit $?
if ! grep -q "href=.*xhtml" ${FSM_URLBASE}/${FOLDER}/toc.xml 2>/dev/null; then
	echo "No documents in ${FOLDER}/toc.xml.  Is the identifier right for this manual type?"
	exit 1
fi

## HTML Docs and the images, PDFs, stylesheets and scripts they use
grep "href=.*xhtml" ${FSM_URLBASE}/${FOLDER}/toc.xml | cut -d\" -f2 | \
	sed -e 's/$/?sisuffix=ff\&locale=en\&siid='"${SIID}"'/' | \
	${SCRIPT_BASE}/tis-fetch.py -i -
RC=$?
[ $RC = 75 ] && exit $RC

# Create JSP static navigation
${SCRIPT_BASE}/toc2html.py ${FSM_URLBASE}/${FOLDER}/toc.xml > ${FSM_URLBASE}/${FOLDER}/toc.html
cp ${BASE}/website-framework/index.html  ${FSM_URLBASE}/${FOLDER}/

exit $RC
