#!/bin/sh
#
# Download Electrical Wiring Diagram docs
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit
fi

# Downloads go through tis-fetch.py, which logs in again if the session expires (you'll be asked for
# the 2FA code) and records progress in $DOWNLOAD_TO/MANIFEST.  Each step below builds a list of URLs
# from files the previous step downloaded, so rerunning this script after a failure skips everything
# already fetched and picks up where it stopped.  Exit status 75 means the session expired and could
# not be renewed, 1 means some files FAILED (see the MANIFEST).

LIST=${TISTMPDIR}/dl-html-ewd.$$
trap 'rm -f ${LIST}' EXIT
FAILED=0

# Fetch the URLs in $LIST.  Wiring diagram pages are shown inside ewd/ewd_index.html, so links in them
# are relative to ewd/ rather than to the page itself.
fetch() {
	# Some contents files have DOS line endings, and an empty name would make a bogus folder URL
	sed -i -e 's/\r//g' -e '/\/\.[a-z0-9]*$/d' -e '/\/-\.[a-z0-9]*$/d' ${LIST}
	[ -s ${LIST} ] || return
	${SCRIPT_BASE}/tis-fetch.py --base ${EWD_URI}/ewd/ "$@" -i ${LIST}
	RC=$?
	[ $RC = 75 ] && exit 75
	[ $RC != 0 ] && FAILED=1
}

##
## Get Wiring Diagrams
##

# The folder is EM#####, EWD##### or (legacy) just #####
for EM in EM${1} EWD${1} ${1}; do
	EWD_URI=/t3Portal/external/en/ewdappu/${EM}
	EWD=${FSM_URLBASE}${EWD_URI}
	echo ${EWD_URI}/xhtml/termdata.xml > ${LIST}
	fetch
	[ -f ${EWD}/xhtml/termdata.xml ] && break
done
if [ ! -f ${EWD}/xhtml/termdata.xml ]; then
	echo "termdata.xml did not download for EM${1}, EWD${1} or ${1}.  Are you sure ${1} is valid?  Exiting."
	exit 1
fi
echo "Wiring diagrams are in ${EWD_URI}"

## Viewer pages, intro, definitions and the per model year contents lists
{
	for F in ewd_index.html print.html intro/intro.html intro/intro.xml intro/repair.html intro/wh-intro.html \
		intro/glossary.html intro/abbre.html intro/guide.html intro/srs_caution.html contents/overall/overall.html \
		defs/indexList.xml defs/common-id.xml defs/sc.xml defs/area.xml \
		styles/loads/ps_cap.xsl styles/connector/partsRefsHtml.xsl styles/connector/termInfo.xsl \
		contents/system/text/svglang.xml contents/connector/connlist.xml contents/connector/parts.xml \
		contents/overall/title.xml contents/relay/title.xml contents/routing/title.xml contents/routing/wire.xml \
		contents/system/title.xml; do
		echo ${EWD_URI}/ewd/${F}
	done
	for i in `seq 1 9`; do
		echo ${EWD_URI}/ewd/icon/zoombar_0${i}.png
	done
	for YYYYMM in `grep yeardata ${EWD}/xhtml/termdata.xml|sed -e 's/^.*startdate="//g'|sed -e 's/".*$//g'`; do
		echo ${EWD_URI}/ewd/contents/connector/locrefs-${YYYYMM}.xml
		echo ${EWD_URI}/ewd/contents/connector/sysrefs-${YYYYMM}.xml
		echo ${EWD_URI}/ewd/contents/loads/ps-${YYYYMM}.xml
		for T in connlist fuselist intro overall root routing system; do
			echo ${EWD_URI}/ewd/contents/tree/${YYYYMM}/tree-${T}.xml
		done
	done
} > ${LIST}
fetch

## Tree pages named in the contents lists.  Repeat in case the new pages name further pages.
for ROUND in 1 2 3 4 5; do
	for YYYYMM in `grep yeardata ${EWD}/xhtml/termdata.xml|sed -e 's/^.*startdate="//g'|sed -e 's/".*$//g'`; do
		for XML in `egrep "(book|note).*id=" ${EWD}/ewd/contents/tree/${YYYYMM}/tree-*.xml 2>/dev/null |sed -e 's/^.*id="//g' | sed -e 's/".*$//g'`; do
			echo ${EWD_URI}/ewd/contents/tree/${YYYYMM}/tree-${XML}.xml
		done
	done | sort -u > ${LIST}
	BEFORE=`find ${EWD}/ewd/contents/tree -name 'tree-*.xml' | wc -l`
	fetch
	AFTER=`find ${EWD}/ewd/contents/tree -name 'tree-*.xml' | wc -l`
	[ ${BEFORE} = ${AFTER} ] && break
done

## Connector, relay, routing, system and overall figures
C=${EWD}/ewd/contents
{
	for SVG in `grep '<fig' ${C}/connector/parts.xml 2>/dev/null |cut -d\> -f2|cut -d\< -f1|sort -u`; do
		echo ${EWD_URI}/ewd/contents/connector/figsvg/${SVG}.svg
		echo ${EWD_URI}/ewd/contents/connector/fig/${SVG}.svgz
	done
	for PNG in `grep 'fig=' ${C}/connector/connlist.xml 2>/dev/null |sed -e 's/^.*fig="//g'|sed -e 's/".*$//g'|sort -u`; do
		echo ${EWD_URI}/ewd/contents/connector/figrepair/${PNG}.png
	done
	for VIDEO in `grep 'video=' ${C}/connector/connlist.xml 2>/dev/null |sed -e 's/^.*video="//g'|sed -e 's/".*$//g'|sort -u`; do
		echo ${EWD_URI}/ewd/contents/connector/video/${VIDEO}.mp4
	done
	for D in relay routing; do
		for SVG in `grep '<fig' ${C}/${D}/title.xml 2>/dev/null |cut -d\> -f2|cut -d\< -f1|sort -u`; do
			echo ${EWD_URI}/ewd/contents/${D}/figsvg/${SVG}.svg
			echo ${EWD_URI}/ewd/contents/${D}/fig/${SVG}.svgz
			echo ${EWD_URI}/ewd/contents/${D}/pdf/${SVG}.pdf
		done
	done
	for SVG in `grep 'svgz' ${C}/system/title.xml 2>/dev/null |cut -d\> -f2|cut -d\< -f1|sort -u`; do
		echo ${EWD_URI}/ewd/contents/system/figsvg/${SVG}.svg
		echo ${EWD_URI}/ewd/contents/system/fig/${SVG}.svgz
	done
	for XML in `grep '<fig' ${C}/system/title.xml 2>/dev/null |cut -d\> -f2|cut -d\< -f1|sort -u`; do
		echo ${EWD_URI}/ewd/contents/system/connect/${XML}.xml
		echo ${EWD_URI}/ewd/contents/system/compact/${XML}.xml
		echo ${EWD_URI}/ewd/contents/system/pdf/${XML}.pdf
	done
	for PDF in `grep '<fig' ${C}/overall/title.xml 2>/dev/null |cut -d\> -f2|cut -d\< -f1|sort -u`; do
		echo ${EWD_URI}/ewd/contents/overall/pdf/${PDF}.pdf
	done
} > ${LIST}
fetch

# Not every system diagram has a compact version; the viewer expects one, so use the full one
for XML in `grep '<fig' ${C}/system/title.xml 2>/dev/null |cut -d\> -f2|cut -d\< -f1|sort -u`; do
	if [ ! -f ${C}/system/compact/${XML}.xml ] && [ -f ${C}/system/connect/${XML}.xml ]; then
		mkdir -p ${C}/system/compact
		cp ${C}/system/connect/${XML}.xml ${C}/system/compact/${XML}.xml
	fi
done

# The viewer shows either figsvg/*.svg or fig/*.svgz depending on the browser.  TIS refuses a few
# .svgz files, so make them from the .svg
for D in connector relay routing system; do
	for SVG in ${C}/${D}/figsvg/*.svg; do
		[ -f "${SVG}" ] || continue
		SVGZ=${C}/${D}/fig/`basename ${SVG} .svg`.svgz
		[ -f ${SVGZ} ] || { mkdir -p ${C}/${D}/fig; gzip -n -c ${SVG} > ${SVGZ}; }
	done
done

[ ${FAILED} = 0 ] || echo "Some files FAILED.  Rerun $0 $1 to retry them; see ${DOWNLOAD_TO}/MANIFEST"
exit ${FAILED}
