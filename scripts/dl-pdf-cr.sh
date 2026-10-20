#!/bin/sh
#
# Download Collision Repair Manual PDFs.  Typically only used with older vehicles (1990~2000)
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

exec ${SCRIPT_BASE}/dl-pdf-any.sh cr/CR${1}
