#!/bin/sh
#
# Download Electrical Wiring Diagram docs
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

if [ x$2 = xEM ]; then
	EM=EM${1}
else
	EM=EWD${1}
fi


##
## Get Wiring Diagrams
##
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/xhtml/termdata.xml
if [ ! -f ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/xhtml/termdata.xml ]; then
	echo "termdata.xml did not download.  Are you sure ${EM} is valid?  Exiting."
	exit
fi
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/ewd_index.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/print.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/intro.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/intro.xml
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/repair.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/wh-intro.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/glossary.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/abbre.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/overall/overall.html
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/defs/indexList.xml
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/defs/common-id.xml
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/defs/sc.xml
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/defs/area.xml
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/styles/loads/ps_cap.xsl
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/styles/connector/partsRefsHtml.xsl

for i in `seq 1 9`; do 
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/EM27J0U/ewd/icon/zoombar_0${i}.png
done

for IMG in `grep img.*src ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/intro/*|sed -e 's/^.*img.*src=//g'|cut -d\" -f2`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/${IMG}
done

for YYYYMM in `grep yeardata ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/xhtml/termdata.xml|sed -e 's/^.*startdate="//g'|sed -e 's/".*$//g'`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/text/svglang.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/connector/parts.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/connector/locrefs-${YYYYMM}.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/connector/sysrefs-${YYYYMM}.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/loads/ps-${YYYYMM}.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/overall/title.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/title.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/title.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/wire.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/title.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-connlist.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-fuselist.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-intro.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-overall.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-root.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-routing.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-system.xml

	for XML in `egrep "(book|note) id=.*file=" ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-*.xml |cut -d\" -f2`; do
		$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/tree/${YYYYMM}/tree-${XML}.xml
	done
done

for SVG in `grep '<fig' ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/connector/parts.xml |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/connector/figsvg/${SVG}.svg
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/connector/fig/${SVG}.svgz
done

for SVG in `grep '<fig' ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/title.xml |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/figsvg/${SVG}.svg
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/fig/${SVG}.svgz
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/relay/pdf/${SVG}.pdf
done

for SVG in `grep '<fig' ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/title.xml |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/figsvg/${SVG}.svg
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/fig/${SVG}.svgz
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/routing/pdf/${SVG}.pdf
done

for SVG in `grep 'svgz' ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/title.xml |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/figsvg/${SVG}.svg
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/fig/${SVG}.svgz
done;

mkdir -p ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/compact
for XML in `grep '<fig' ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/title.xml |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/connect/${XML}.xml
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/compact/${XML}.xml
	if [ ! -f ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/compact/${XML}.xml ]; then
		cp ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/connect/${XML}.xml ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/compact/${XML}.xml
	fi
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/system/pdf/${XML}.pdf
done

for PDF in `grep '<fig' ${FSM_URLBASE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/overall/title.xml |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	$WG ${WEBSITE}/t3Portal/external/en/ewdappu/${EM}/ewd/contents/overall/pdf/${PDF}.pdf
done

