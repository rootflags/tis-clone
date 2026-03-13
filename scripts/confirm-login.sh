#!/bin/sh

. ${HOME}/.tis/tis-clone.cfg

TESTPAGE="/t3Portal/staticcontent/en/techinfo/docs/glossary.pdf"

${WG_NOMIRROR} -O ${TISTMPDIR}/tis-testpage.out ${WEBSITE}/$TESTPAGE > /dev/null 2>&1

grep "Subscription Level" ${TISTMPDIR}/tis-testpage.out > /dev/null 2>&1
if [ $? = 0 ]; then
	echo "Detected 'Subscription Level' web page prompt.  Are you sure you're logged in?"
	echo "Run ${SCRIPT_BASE}/tis-login.sh and try again"
	rm -f ${TISTMPDIR}/tis-testpage.out
	exit 1
fi

rm -f ${TISTMPDIR}/tis-testpage.out
