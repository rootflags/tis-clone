#!/bin/sh
#
# Download all of the website framework
#
# Uses tis-fetch.py (see dl-html-ewd.sh), so rerunning it resumes and skips files already in the
# MANIFEST.  The ewd.js and all-t3.js patches below are redone on every run from the saved .orig, so
# this can run before or after the wiring diagram download.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

LIST=${TISTMPDIR}/dl-framework.$$
trap 'rm -f ${LIST}' EXIT

# Set up local website framework CSS
cp -a ${BASE}/website-framework/* ${FSM_URLBASE}/

{
	# Patched below
	echo /t3Portal/external/en/ewdappu/system/js/ewd/ewd.js
	echo /t3Portal/framework/skins/t3/js/all-t3.js

	# Wiring Diagram framework.  The viewer loads these scripts itself, so they aren't found as page links.
	for F in ewdappu/index.jsp ewdappu/pdrSelect.html \
		external/en/ewdappu/system/js/ewd/EMUtil.js external/en/ewdappu/system/js/ewd/dict_ewdconst.js \
		external/en/ewdappu/system/js/ewd/dict_ewdmessage.js external/en/ewdappu/system/js/ewd/lib/EWDPrint.js \
		external/en/ewdappu/system/js/ewd/lib/WireList.js external/en/ewdappu/system/js/ewd/lib/domparser.js \
		external/en/ewdappu/system/js/ewd/fig/svgfig.js staticcontent/js/t3StaticContentCommon.js \
		portlets/tis/document/myFavorite/addLastVisitedDocs.do; do
		echo /t3Portal/${F}
	done

	# Shared navigation images
	for F in empty page pagesel folder foldersel folderopen plus minus; do
		echo /t3Portal/resources/jsp/siviewer/icons/${F}.gif
	done
	for F in english_selected spanish_selected french_selected english_available spanish_available \
		french_available en_unavailable es_unavailable fr_unavailable; do
		echo /t3Portal/resources/images/language/en/${F}.png
	done
	echo /favicon.ico
	for F in stylegraphics/clear.gif stylegraphics/header-left.gif stylegraphics/header-right.gif \
		resources/jsp/images/clear.gif resources/jsp/siviewer/icons/tis.png; do
		echo /t3Portal/${F}
	done

	# The TIS siviewer navigation pages (resources/jsp/siviewer/*.jsp) aren't needed: each manual gets its
	# own navigation from toc2html, and only the siviewer icons above are used.
} > ${LIST}

# favicon.ico lives outside /t3Portal/
${SCRIPT_BASE}/tis-fetch.py --scope / -i ${LIST}
RC=$?
[ $RC = 75 ] && exit 75

# Rewrite $1 from $1.orig with sed expression $3.  $2 is text only the patched file contains, so a
# freshly downloaded (unpatched) file gets moved to .orig first.
patch() {
	F=${FSM_URLBASE}$1
	[ -f ${F} ] || return
	grep -qF "$2" ${F} || mv -f ${F} ${F}.orig
	[ -f ${F}.orig ] && sed -e "$3" ${F}.orig > ${F}
}

# ewd.js requires a change to force using the uncompressed SVG images.
patch /t3Portal/external/en/ewdappu/system/js/ewd/ewd.js 'ElY.EsZ="/figsvg";ElY.Esa=".svg";ElY.Esb' \
	's;ElY.EsZ="/fig";ElY.EsZ="/figsvg";g; s;ElY.Esa=".svgz";ElY.Esa=".svg";g; s;Ejx.EsZ="/fig";Ejx.EsZ="/figsvg";g; s;Ejx.Esa=".svgz";Ejx.Esa=".svg";g'

patch /t3Portal/framework/skins/t3/js/all-t3.js '//self.AJAX.setRequestHeader("Connection"' \
	's;self.AJAX.setRequestHeader("Connection";//self.AJAX.setRequestHeader("Connection";g'

# Actual website is missing this image, so let's include it to make the results better
if [ ! -f ${FSM_URLBASE}/t3Portal/stylegraphics/clear.gif ] && [ -f ${FSM_URLBASE}/t3Portal/resources/jsp/images/clear.gif ]; then
	mkdir -p ${FSM_URLBASE}/t3Portal/stylegraphics
	cp ${FSM_URLBASE}/t3Portal/resources/jsp/images/clear.gif ${FSM_URLBASE}/t3Portal/stylegraphics/
fi

[ $RC = 0 ] || echo "Some files FAILED.  Rerun $0 to retry them; see ${DOWNLOAD_TO}/MANIFEST"
exit $RC
