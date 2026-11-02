#!/bin/sh
#
# Create index.html for PDFs
#
# Usage:
#   build-pdfidx.sh [FOLDER] > FOLDER/PDFs/index.html
#
# FOLDER is the website folder that holds PDFs/ (ie: $DOWNLOAD_TO/techinfo.toyota.com) or the download folder
# above it.  Without it, FSM_URLBASE from ~/.tis/tis-clone.cfg.  Only *.pdf files are listed, so a .part
# file left by an interrupted run isn't.
#

. ${HOME}/.tis/tis-clone.cfg

SITE=${1:-${FSM_URLBASE}}
[ -d "${SITE}/PDFs" ] || [ ! -d "${SITE}/techinfo.toyota.com/PDFs" ] || SITE=${SITE}/techinfo.toyota.com
if [ ! -d "${SITE}/PDFs" ]; then
	echo "$0: no PDFs folder in ${SITE}" >&2
	exit 1
fi

# Text for HTML
esc() {
	printf '%s' "$1" | sed -e 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g'
}

echo '<!DOCTYPE html><html><head><title>PDF Files</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <link rel="stylesheet" href="/framework/bootstrap.min.css">
  </head>
  <body style="padding:0px; margin:0px;">
  <img src="/t3Portal/resources/images/globals/header/headerbar.bg.blu.gif" style="width:100%; height:40px; margin:0px; border:0px; padding:0px">
  <ul class="nav flex-column flex-nowrap">'

cd "${SITE}" || exit 1
sub1=0
find PDFs -mindepth 1 -maxdepth 1 -type d | sort | while read -r FOLDER
do
	sub1=`expr $sub1 + 1`
	TITLE=`esc "${FOLDER#PDFs/}"`
	FOLDER_URL=`printf '%s' "${FOLDER}" | sed -e 's/%/%25/g; s/ /%20/g; s/#/%23/g; s/&/\&amp;/g; s/"/%22/g'`
	echo "    <li class=\"nav-item drop\">"
	echo "    <a class=\"nav-link collapsed\" href=\"#submenu${sub1}\" data-toggle=\"collapse\" >+ ${TITLE}</a>"
	echo "    <div class=\"collapse\" id=\"submenu${sub1}\" aria-expanded=\"false\">"
	echo "    <ul class=\"flex-column nav\" style=\"padding:0px 0px 0px 40px;\">"
	for P in "${FOLDER}"/*.pdf; do
		[ -f "${P}" ] || continue
		PDF=${P##*/}
		PDF_URL=`printf '%s' "${PDF}" | sed -e 's/%/%25/g; s/ /%20/g; s/#/%23/g; s/&/\&amp;/g; s/"/%22/g'`
		echo "      <li class=\"nav-item\"><a class=\"nav-link py-0\" href=\"/${FOLDER_URL}/${PDF_URL}\" target=\"new\"><i class=\"fa fa-fw fa-clock-o\"></i>- `esc "${PDF}"`</a></li>"
	done
	echo "    </ul></div>"
done
echo '</ul>
<script src="/framework/jquery-3.4.1.min.js"></script>
<script src="/framework/popper.min.js"></script>
<script src="/framework/bootstrap.min.js"></script>
</body>'
