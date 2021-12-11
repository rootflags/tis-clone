#!/bin/sh
#
# Convert XHTML files to PDFs
#

. tis-clone.cfg

OPTIONS="--keep-relative-links"

if [ x$1 = x ]; then
	echo "Syntax: $0 rm/RM08F0U"
	exit
fi

for f in `ls *.html | cut -d. -f1`; do
	wkhtmltopdf ${OPTIONS} ${MYURL}/t3Portal/document/${1}/xhtml/${f}.html ${f}.pdf
done
