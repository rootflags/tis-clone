#!/bin/sh
#
# Download Body Repair Manualdocs
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

i=$1
FOLDER="/t3Portal/external/en/cr/BM${i}"

${SCRIPT_BASE}/dl-html-inc.sh "${FOLDER}"

# Sometimes the PDF files are really an HTML redirect inside a Javascript bit.  In that case we'll re-process
# the "PDF" files to download the correct PDF file if they're not really a PDF
cd $DOWNLOAD_TO
FOLDER="t3Portal/document/cr/BM${i}"
find ${FSM_URLBASE}/${FOLDER} -name "*.pdf" | while read -r FILE
do
	echo * PROCESSING $FILE
	file "$FILE" | grep HTML> /dev/null 2>&1
	if [ $? = 0 ]; then
		PDF=`cat $FILE |sed -e 's/\.pdf.*$//g'|awk -F\' '{print $NF}'`
		$WG -q ${WEBSITE}${PDF}.pdf\?sisuffix=ff\&locale=en\&siid=1640203137875
		file "${FSM_URLBASE}/${PDF}.pdf?sisuffix=ff&locale=en&siid=1640203137875" | grep PDF
		if [ $? = 0 ]; then
			rm -f "$FILE"
			mv -f "${FSM_URLBASE}/${PDF}.pdf?sisuffix=ff&locale=en&siid=1640203137875" "$FILE"
		fi
	fi
done
