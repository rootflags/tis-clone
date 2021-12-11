#!/bin/sh
#
# Sample script 
#

. /etc/tis-clone.cfg

echo "Sample only right now"
exit
for f in `ls *.html | cut -d. -f1`; do 
	wkhtmltopdf ${MYURL}/t3Portal/document/cr/BM27J0U/xhtml/${f}.html ${f}.pdf 
done  

$GS -sOutputFile=${MYURL_BASE}/TOYOTA/LAND_CRUISER/J200/PDFs/BodyRepair_BM27J0U_2018.pdf `grep xhtml ${MYURL}/resources/jsp/BM27J0U/nav2018.jsp |sed -e "s/'/\n/g"|grep t3Portal|sed -e 's/html?locale=en/pdf/g'|sed -e "s;^;${MYURL_BASE};g"|xargs`


