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

if [ ! -d "t3Portal" ]; then
	echo "You must run this from the root where folder t3Portal is located"
	exit
fi

echo "Checking if any XHTML files listed in any toc.xml are missing"
for TOC in `find . -name toc.xml`; do
	for F in `cat $TOC|grep href=.*xhtml|sed -e 's/">.*$//g'|awk -F\" '{print $NF}'`; do
		if [ ! -f ${PWD}${F} ]; then
			echo Missing: ${PWD}${F}
		fi
	done
done

# Look for pages where download failed
echo "Checking if any downloaded files failed due to expired or invalid cookies..."
grep -r "TIS is your service support source" * |cut -d: -f1

