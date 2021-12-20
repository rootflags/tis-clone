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
	#cat ${MYURL_BASE}/t3Portal/document/${1}/xhtml/${f}.html | sed -e 's/\.html/.pdf/g' > ${MYURL_BASE}/t3Portal/document/${1}/xhtml/NEW-${f}.html
	echo "* Converting ${f}.html ($I of $COUNT)";
	wkhtmltopdf ${OPTIONS} ${MYURL_BASE}/t3Portal/document/${1}/xhtml/${f}.html ${f}.pdf
	#rm -f ${MYURL_BASE}/t3Portal/document/${1}/xhtml/NEW-${f}.html
done

