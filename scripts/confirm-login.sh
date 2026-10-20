#!/bin/sh
#
# Confirm the saved session works before downloading.  Fetches a small subscriber-only PDF and
# checks the ways it can fail:
#  - not logged in: TIS serves its "Subscription Level" page instead of the PDF
#  - logged in elsewhere: only one session per account is allowed, so a browser login kills this
#    one and vice versa.  TIS then redirects either to concurrentLoginFailure.html (issue #11) or,
#    if the sign-on session itself was ended, back to its login page.
# The checks live in tis-fetch.py, which the downloaders use for every file.  Exit status 0 if the
# session works, 75 if not.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

exec ${SCRIPT_BASE}/tis-fetch.py --check -q
