#!/bin/sh
#
# Download any page with wget
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [URI]"
	echo "    ie: $0 /t3Portal/index.jsp"
	echo "  will recursively download using the WEBSITE parameter in the /etc/tis-clone.cfg file,"
	echo "    ie: https://techinfo.toyota.com/t3Portal/index.jsp"
	exit
fi

URL=$1

##
## Recursively download pages
##
$WG ${WEBSITE}/${URL}

