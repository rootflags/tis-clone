#!/bin/sh
#
# Try to download any missed PDFs
#

. tis-clone.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

i=$1
BM=BM${i}
EM=EM${i}
RM=RM${i}
NM=NM${i}


##
## Get Repair Manual 
##

## TOC
$WG ${WEBSITE}/t3Portal/external/en/rm/${RM}/toc.xml

## HTML Docs and Images/PDFs
for DOC in `grep "href=.*xhtml" ${FSM_URLBASE}/t3Portal/external/en/rm/${RM}/toc.xml |cut -d\" -f2`; do
	URL=`echo ${DOC} | sed -e 's/$/\?sisuffix=ff\&locale=en\&siid=1520435234586/g'`;
	$WG "${WEBSITE}/${URL}"
	mv -f ${FSM_URLBASE}/${URL} ${FSM_URLBASE}/${DOC}
done


##
## Get Wiring Diagram PDFs
##
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/print.html

for f in `ls -1 ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/connect/|sed -e 's/.xml/.pdf/g'`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/pdf/${f}
done

for f in `ls -1 ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/figsvg/|sed -e 's/.svg/.pdf/g'`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/pdf/${f}
done

for f in `ls -1 ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/figsvg/|sed -e 's/.svg/.pdf/g'`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/pdf/${f}
done
