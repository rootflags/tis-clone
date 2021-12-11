#!/bin/sh
#
# Download Body Repair Manual PDFs.  Typically only used with older vehicles (1990~2000)
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

i=$1
BR=BR${i}

##
## Get Repair Manual 
##

## TOC
$WG ${WEBSITE}/t3Portal/external/en/cr/${BR}/toc.xml

## HTML Docs and Images/PDFs
for DOC in `grep "href=.*xhtml" ${FSM_URLBASE}/t3Portal/external/en/cr/${BR}/toc.xml |cut -d\" -f2`; do
	URL=`echo ${DOC} | sed -e 's/$/\?sisuffix=ff\&locale=en\&siid=1520435234586/g'`;
	$WG "${WEBSITE}/${URL}"
	mv -f ${FSM_URLBASE}/${URL} ${FSM_URLBASE}/${DOC}
	PDF=`grep PDF ${FSM_URLBASE}/${DOC} |grep -v "link rel"|cut -d\" -f2`
	$WG "${WEBSITE}/${PDF}?sisuffix=ff&locale=en&siid=1520435234586"
	mv -f ${FSM_URLBASE}/${PDF}\?sisuffix=ff\&locale=en\&siid=1520435234586 ${FSM_URLBASE}/${PDF}
done

