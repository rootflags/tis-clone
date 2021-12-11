#!/bin/sh
#
# Convert Repair Manual HTML webpages to PDFs
#

. tis-clone.cfg

OPTIONS="--keep-relative-links"

cd ${MYURL_BASE}/t3Portal/document/rm

for folder in $*; do
	echo "Processing $folder"
	cd ${folder}/xhtml 
	for f in `ls *.html | cut -d. -f1`; do
		wkhtmltopdf ${OPTIONS} ${MYURL}/t3Portal/document/rm/${folder}/xhtml/${f}.html ${f}.pdf
	done 
	cd ../../ 
done

