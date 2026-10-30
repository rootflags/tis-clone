#!/bin/sh
#
# Download all of the website framework
#
# Uses tis-fetch.py (see dl-html-ewd.sh), so rerunning it resumes and skips files already in the
# MANIFEST.  The ewd.js, svgfig.js, index.jsp and all-t3.js patches below are redone on every run from
# the saved .orig, so this can run before or after the wiring diagram download.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

LIST=${TISTMPDIR}/dl-framework.$$
trap 'rm -f ${LIST}' EXIT

# Set up local website framework CSS.  Not website-framework/index.html: that's each manual's frame page
# (dl-html-inc.sh copies it), and here it would replace build-index.py's front page.
cp -a ${BASE}/website-framework/framework ${BASE}/website-framework/main.html ${FSM_URLBASE}/

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
	# The TIS stylesheet; its images include the header bar that build-index.py and build-pdfidx.sh use
	echo /t3Portal/framework/skins/t3/css/all-t3.css
	echo /favicon.ico
	for F in stylegraphics/clear.gif stylegraphics/header-left.gif stylegraphics/header-right.gif \
		resources/jsp/images/clear.gif resources/jsp/siviewer/icons/tis.png; do
		echo /t3Portal/${F}
	done

	# The TIS siviewer navigation pages (resources/jsp/siviewer/*.jsp) aren't needed: each manual gets its
	# own navigation from toc2html.py, and only the siviewer icons above are used.
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

# The wiring diagram viewer gets a link back to the front page, left of its Back button
patch /t3Portal/ewdappu/index.jsp 'title="Home"' \
	's|<td class="left-align" id="back"|<td style="vertical-align:top;"><a href="/index.html" target="_top" title="Home" style="font:bold 9pt Arial, sans-serif; color:black; text-decoration:none; white-space:nowrap; padding:0px 8px;">\&lt; Home</a></td>&|'

# Safari (Mac and every iOS browser) reloads an embedded SVG each time its <embed>'s width or height is
# set, even to the same value.  The viewer sets them after every load, so Safari reloads forever and the
# wiring diagram page stays blank.  Only set them when they change.
patch /t3Portal/external/en/ewdappu/system/js/ewd/fig/svgfig.js 'if(this.EtV.getAttribute("width")!=Evw+"px")' \
	's|EtP.prototype.Evy=function(Evw,Elw){try{this.EtV.setAttribute("width",Evw+"px");this.EtV.setAttribute("height",Elw+"px");|EtP.prototype.Evy=function(Evw,Elw){try{if(this.EtV.getAttribute("width")!=Evw+"px"){this.EtV.setAttribute("width",Evw+"px");}if(this.EtV.getAttribute("height")!=Elw+"px"){this.EtV.setAttribute("height",Elw+"px");}|'

patch /t3Portal/framework/skins/t3/js/all-t3.js '//self.AJAX.setRequestHeader("Connection"' \
	's;self.AJAX.setRequestHeader("Connection";//self.AJAX.setRequestHeader("Connection";g'

# Actual website is missing this image, so let's include it to make the results better
if [ ! -f ${FSM_URLBASE}/t3Portal/stylegraphics/clear.gif ] && [ -f ${FSM_URLBASE}/t3Portal/resources/jsp/images/clear.gif ]; then
	mkdir -p ${FSM_URLBASE}/t3Portal/stylegraphics
	cp ${FSM_URLBASE}/t3Portal/resources/jsp/images/clear.gif ${FSM_URLBASE}/t3Portal/stylegraphics/
fi

[ $RC = 0 ] || echo "Some files FAILED.  Rerun $0 to retry them; see ${DOWNLOAD_TO}/MANIFEST"
exit $RC
