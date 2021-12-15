#!/bin/sh
#
# Download Collision Repair Manual docs
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

i=$1
FOLDER="/t3Portal/external/en/cr/CR${i}"

${SCRIPT_BASE}/dl-html-inc.sh "${FOLDER}"

