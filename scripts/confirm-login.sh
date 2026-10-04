#!/bin/sh
#
# Confirm the saved session works before downloading.  Fetches a small subscriber-only PDF and
# checks two ways it can fail:
#  - not logged in: TIS serves its "Subscription Level" page
#  - logged in elsewhere: only one session per account is allowed, so a browser login kills this
#    one and vice versa.  TIS then redirects either to concurrentLoginFailure.html (issue #11) or,
#    if the sign-on session itself was ended, back to its login page.
#

. ${HOME}/.tis/tis-clone.cfg

TESTPAGE="/t3Portal/staticcontent/en/techinfo/docs/glossary.pdf"
OUT=${TISTMPDIR}/tis-testpage.out
LOG=${TISTMPDIR}/tis-testpage.log

${WG_NOMIRROR} -O ${OUT} ${WEBSITE}/$TESTPAGE > ${LOG} 2>&1

if grep -qE 'concurrentLoginFailure|techInfoPortal/login' ${LOG}; then
	echo "TIS rejected the session: it expired, or the account is logged in somewhere else."
	echo "Log out of TIS in any browser, then run ${SCRIPT_BASE}/tis-login.sh and try again"
	rm -f ${OUT} ${LOG}
	exit 1
fi

grep "Subscription Level" ${OUT} > /dev/null 2>&1
if [ $? = 0 ] || [ "`head -c 4 ${OUT} 2>/dev/null`" != "%PDF" ]; then
	echo "Detected 'Subscription Level' web page prompt.  Are you sure you're logged in?"
	echo "Run ${SCRIPT_BASE}/tis-login.sh and try again"
	rm -f ${OUT} ${LOG}
	exit 1
fi

rm -f ${OUT} ${LOG}
