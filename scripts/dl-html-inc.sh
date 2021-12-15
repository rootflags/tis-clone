#!/bin/sh
#
# Download Body Repair Manualdocs
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [WEBSITE URI PATH]"
	echo "    ie: $0 /t3Portal/external/en/bm/BM27J0U"
	exit
fi

FOLDER=$1

##
## Get Repair Manual 
##

## TOC
$WG ${WEBSITE}/${FOLDER}/toc.xml

## HTML Docs and Images/PDFs
for DOC in `grep "href=.*xhtml" ${FSM_URLBASE}/${FOLDER}/toc.xml |cut -d\" -f2`; do
	URL=`echo ${DOC} | sed -e 's/$/\?sisuffix=ff\&locale=en\&siid=1520435234586/g'`;
	$WG "${WEBSITE}/${URL}"
	mv -f ${FSM_URLBASE}/${URL} ${FSM_URLBASE}/${DOC}
done

# Create JSP static navigation
if [ -f ${FSM_URLBASE}/${FOLDER}/toc.xml ]; then
	${SCRIPT_BASE}/toc2html ${FSM_URLBASE}/${FOLDER}/toc.xml > ${FSM_URLBASE}/${FOLDER}/toc.html
	cp ${BASE}/website-framework/index.html  ${FSM_URLBASE}/${FOLDER}/
fi

