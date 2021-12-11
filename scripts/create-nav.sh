#!/bin/sh
# 
# Create Navigation files.  Part of a (currently manual) process to create HTML index pages
#

. tis-clone.cfg

JSP=/t3Portal/resources/jsp

if [ x$1 = x ]; then
	echo "Syntax: $0 toc.xml"
	exit
fi

TITLE=`grep '<name>' "$1" | head -1|cut -d\> -f2|cut -d\< -f1`
MANUAL=`grep '<name>' "$1" | head -1|cut -d\( -f2|cut -d\) -f1`

for WORD in `echo "$TITLE"`; do 
	YEAR=`echo "$WORD" | grep -w "[12]0[0-9][0-9]"`
	if [ x$YEAR != x ]; then break; fi
done

HREF=`grep 't3Portal' "$1" | head -1|cut -d\" -f2`
for F in `echo "$HREF" | sed -e 's;/; ;g'`; do
	if [ $F = $MANUAL ]; then break; fi
	FDIR=$F
done

mkdir -p ${FSM_URLBASE}/${JSP}/${MANUAL}
${SCRIPT_BASE}/toc2nav "$1" > ${FSM_URLBASE}/${JSP}/${MANUAL}/nav.idx

cp -a ${FSM_URLBASE}/${JSP}/siviewer.template/default.html ${FSM_URLBASE}/${JSP}/${MANUAL}/
cp -a ${FSM_URLBASE}/${JSP}/siviewer.template/icons ${FSM_URLBASE}/${JSP}/${MANUAL}/
cp -a ${FSM_URLBASE}/${JSP}/siviewer.template/siviewerload.js ${FSM_URLBASE}/${JSP}/${MANUAL}/
cp -a ${FSM_URLBASE}/${JSP}/siviewer.template/siviewermenu.js ${FSM_URLBASE}/${JSP}/${MANUAL}/
cp -a ${FSM_URLBASE}/${JSP}/siviewer.template/top_menu.jsp ${FSM_URLBASE}/${JSP}/${MANUAL}/
cp -a ${FSM_URLBASE}/${JSP}/siviewer.template/tree.js ${FSM_URLBASE}/${JSP}/${MANUAL}/
cat ${FSM_URLBASE}/${JSP}/siviewer.template/index.jsp.tmpl | sed -e "s/REPLACE_TITLE/$TITLE/g" > ${FSM_URLBASE}/${JSP}/${MANUAL}/index.jsp
cat ${FSM_URLBASE}/${JSP}/siviewer.template/nav.jsp.tmpl-1 \
		${FSM_URLBASE}/${JSP}/${MANUAL}/nav.idx \
		${FSM_URLBASE}/${JSP}/siviewer.template/nav.jsp.tmpl-2 | \
		sed -e "s/REPLACE_TITLE/$TITLE/g" | \
		sed -e "s/REPLACE_DIR/$MANUAL/g" | \
		sed -e "s/REPLACE_TYPE/$FDIR/g" | \
		sed -e "s/REPLACE_YEAR/$YEAR/g" > ${FSM_URLBASE}/${JSP}/${MANUAL}/nav.jsp
