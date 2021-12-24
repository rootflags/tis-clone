#!/bin/sh
#
# Convert XHTML files to PDFs
#

. /etc/tis-clone.cfg

OPTIONS="--keep-relative-links -q"

if [ x$1 = x ]; then
	echo "Syntax: $0 rm/RM08F0U"
	exit
fi

# Must be run from the xhtml folder!
COUNT=`ls *.html|wc -l`
I=0

# wjhtmltopdf will try to use web paths.  If the root web path does not match our root path, 
# create a temporary symlink so that wkhtmltopdf works.
if [ ! -e /t3Portal ]; then
	ln -s ${MYURL_BASE}/t3Portal /t3Portal
	WKPATH=${MYURL_BASE}
	# add a sleep because sometimes the above path creation gets cached and the next test fails
	sleep 1
fi

# If symlink creation didn't work, then 
if [ ! -e /t3Portal ]; then
	curl -Is ${MYURL}/t3Portal/staticcontent/js/t3StaticContentCommon.js|grep "200 OK" >/dev/null 2>&1
	if [ $? = 0 ]; then
		WKPATH=${MYURL}
	fi
fi

if [ x${WKPATH} = x ]; then
	echo "Cannot create /t3Portal or access ${MYURL}.  Images will not generate.  Exiting"
	exit
fi

echo Using $WKPATH
for f in `ls *.html | cut -d. -f1`; do
	I=`expr $I + 1`
	echo "* Converting $PWD/${f}.html ($I of $COUNT)";
	wkhtmltopdf ${OPTIONS} ${MYURL_BASE}/t3Portal/document/${1}/xhtml/${f}.html ${f}.pdf
	if [ ! -f ${f}.pdf ]; then
		PDF=`cat ${FSM_URLBASE}/t3Portal/document/${1}/xhtml/${f}.html |grep application/pdf|sed -e 's/\.pdf.*$//g'|awk -F\" '{print $NF}'`
		if [ -f  "${FSM_URLBASE}/${PDF}.pdf" ]; then
			echo "  - Conversion failed, using ${FSM_URLBASE}/${PDF}.pdf" 
			cp -a "${FSM_URLBASE}/${PDF}.pdf" ${f}.pdf
		fi
	fi
done

rm -f /t3Portal
