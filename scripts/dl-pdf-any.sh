#!/bin/sh
#
# Download any type of PDF section.  You shouldn't normally need this script
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [type]/[GSIC_CODE]"
	echo "    ie: $0 rm/RM27J0U"
	exit
fi

MANUAL=$1

##
## Get Repair Manual 
##

## TOC
$WG ${WEBSITE}/t3Portal/external/en/${MANUAL}/toc.xml

## HTML Docs and Images/PDFs
for DOC in `grep "href=.*xhtml" ${FSM_URLBASE}/t3Portal/external/en/${MANUAL}/toc.xml |cut -d\" -f2`; do
	URL=`echo ${DOC} | sed -e 's/$/\?sisuffix=ff\&locale=en\&siid=1520435234586/g'`;
	$WG "${WEBSITE}/${URL}"
	mv -f ${FSM_URLBASE}/${URL} ${FSM_URLBASE}/${DOC}
	PDF=`grep PDF ${FSM_URLBASE}/${DOC} |grep -v "link rel"|cut -d\" -f2`
	$WG "${WEBSITE}/${PDF}?sisuffix=ff&locale=en&siid=1520435234586"
	mv -f ${FSM_URLBASE}/${PDF}\?sisuffix=ff\&locale=en\&siid=1520435234586 ${FSM_URLBASE}/${PDF}
done

