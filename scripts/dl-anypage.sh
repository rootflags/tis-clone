#!/bin/sh
#
# Download any TIS page, plus the images, stylesheets, scripts and PDFs it uses
#
# Uses tis-fetch.py, so it logs in again if the session expires and records the files in the MANIFEST.
# Unlike the wget mirror this script used to run, it doesn't follow links to other pages; list each
# page you want, or use a dl-html-*.sh script to download a whole manual.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 [URI] ..."
	echo "    ie: $0 /t3Portal/index.jsp"
	echo "  will download the page and what it uses, from the WEBSITE parameter in the ${HOME}/.tis/tis-clone.cfg file,"
	echo "    ie: https://techinfo.toyota.com/t3Portal/index.jsp"
	exit
fi

exec ${SCRIPT_BASE}/tis-fetch.py --scope / "$@"
