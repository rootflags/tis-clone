#!/bin/sh
#
# Download any type of PDF section.  You shouldn't normally need this script
#
# Older manuals are a toc.xml of small xhtml pages that each link to a PDF.  dl-html-inc.sh fetches the
# pages and the PDFs they link to with tis-fetch.py, including the PDFs that TIS hides behind a
# "?locale=" redirect page, so it resumes and logs in again like the other downloaders.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ x$1 = x ]; then
	echo "Syntax: $0 [type]/[GSIC_CODE]"
	echo "    ie: $0 rm/RM27J0U"
	exit
fi

exec ${SCRIPT_BASE}/dl-html-inc.sh /t3Portal/external/en/$1
