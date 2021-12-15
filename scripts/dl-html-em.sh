#!/bin/sh
#
# Download Electrical Manual docs
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

${SCRIPT_BASE}/dl-html-ewd.sh $1 "EM"
