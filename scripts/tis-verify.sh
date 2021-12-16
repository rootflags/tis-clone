#!/bin/sh
#
# This script will show you any files that failed to download correctly due to the session cookie expiring 
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	cd ${FSM_URLBASE}
else
	cd $1
fi
grep -r "TIS is your service support source" * 
