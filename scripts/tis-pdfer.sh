#!/bin/sh
#
# Convert HTML Manual webpages to PDFs.  
#  * Works OK with BM/CR, RM, and NM/NCF docs
#  * Doesn't work with EM/EWDs as they need a different process
#  * Links in the PDFs will point to the website path so they won't work locally unless you have all your docs
#    in /t3Portal
#

. /etc/tis-clone.cfg

OPTIONS="--keep-relative-links"

cd ${MYURL_BASE}

# Iterate through all the XHTML folders 
for folder in `find t3Portal/document/ -name xhtml -type d`; do
	echo "Processing $folder"
	pdfdir=`echo $folder | sed -e 's;/xhtml;/pdf;g'`
	mkdir -p $pdfdir

	# Get all HTML files, convert links to PDF targets, then crreate PDF files
	for ffull in `ls $folder/*.html | cut -d. -f1`; do
		fshort=`echo $ffull|awk -F/ '{print $NF}'`
		cat ${ffull}.html | sed -e 's/\.html/.pdf/g' > ${TMPDIR}/${fshort}.html
		wkhtmltopdf ${OPTIONS} ${TMPDIR}/${fshort}.html $pdfdir/${fshort}.pdf
		rm -f ${TMPDIR}/${fshort}.html
	done 
done

