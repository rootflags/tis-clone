#!/bin/sh
#
# This script will show you any files that failed to download correctly due to the session cookie expiring 
#

. tis-clone.cfg

cd ${FSM_URLBASE}
grep -r "TIS is your service support source" * 
