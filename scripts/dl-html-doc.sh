#!/bin/sh
#
# Download any HTML publication by its full name, wherever TIS keeps it
#
# For the manuals that don't fit a section's prefix and code: ie: the A340 automatic transmission manual
# (RM479U, in atm/), OBD II (OTH021U, in rm/) and older collision manuals (BRM080U, CR02X, in cr/).
# tis-lookup.py lists them as tis-clone --doc PUB.  The folder is the first of rm/, atm/, cr/ and ncf/ that
# has PUB/toc.xml, already downloaded (tis-clone's probe) or asked of TIS.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 PUBLICATION"
	echo "    ie: $0 RM479U"
	exit 1
fi

EN=/t3Portal/external/en
for T in rm atm cr ncf; do
	[ -f ${FSM_URLBASE}${EN}/${T}/$1/toc.xml ] && exec ${SCRIPT_BASE}/dl-html-inc.sh ${EN}/${T}/$1
done
for T in rm atm cr ncf; do
	${SCRIPT_BASE}/tis-fetch.py -q --no-requisites ${EN}/${T}/$1/toc.xml
	RC=$?
	[ $RC = 75 ] && exit 75
	[ -f ${FSM_URLBASE}${EN}/${T}/$1/toc.xml ] && exec ${SCRIPT_BASE}/dl-html-inc.sh ${EN}/${T}/$1
done
echo "TIS has no $1 in rm/, atm/, cr/ or ncf/"
exit 1
