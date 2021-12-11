#!/bin/sh
#
# Download Repair Manual
#

. tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

i=$1
RM=RM${i}

##
## Get Repair Manual 
##

## TOC
$WG ${WEBSITE}/t3Portal/external/en/rm/${RM}/toc.xml

## HTML Docs and Images/PDFs
for DOC in `grep "href=.*xhtml" ${FSM_URLBASE}/t3Portal/external/en/rm/${RM}/toc.xml |cut -d\" -f2`; do
	URL=`echo ${DOC} | sed -e 's/$/\?sisuffix=ff\&locale=en\&siid=1520435234586/g'`;
	$WG --reject-regex='linkId=*' "${WEBSITE}/${URL}"
	mv -f ${FSM_URLBASE}/${URL} ${FSM_URLBASE}/${DOC}
done

