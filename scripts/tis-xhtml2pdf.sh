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
for f in `ls *.html | cut -d. -f1`; do
	I=`expr $I + 1`
	echo "* Converting $PWD/${f}.html ($I of $COUNT)";
	wkhtmltopdf ${OPTIONS} ${MYURL_BASE}/t3Portal/document/${1}/xhtml/${f}.html ${f}.pdf
	if [ ! -f ${f}.pdf ]; then
		PDF=`cat ${FSM_URLBASE}/t3Portal/document/${1}/xhtml/${f}.html |grep application/pdf|sed -e 's/\.pdf.*$//g'|awk -F\" '{print $NF}'`
		cp -a "${FSM_URLBASE}/${PDF}.pdf" ${f}.pdf
	fi
done

