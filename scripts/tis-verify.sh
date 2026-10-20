#!/bin/sh
#
# This script will show you any files that failed to download correctly due to the session cookie expiring
# (and other bad downloads).  See tis-verify.py, which does the work, for the details and options.
#

. ${HOME}/.tis/tis-clone.cfg

exec ${SCRIPT_BASE}/tis-verify.py "$@"
