#!/bin/sh
#
# Initial setup script
#


FOLDER=`dirname $0`
if [ -f ${HOME}/.tis/tis-clone.cfg ]; then
	CFG=${HOME}/.tis/tis-clone.cfg
else 
	CFG=$FOLDER/tis-clone.cfg
fi
. $CFG
. $FOLDER/scripts/tis-log.sh
echo "Loaded tis-clone.cfg defaults from $CFG"

echo "Checking dependencies..."
# Confirm we have all the basic packages required
for cmd in bash cat cp curl cut diff find grep gzip head ls mkdir mv python3 rm rmdir sed sort xargs gs pdfinfo pdfseparate pdftk rsync wkhtmltopdf; do
	which $cmd > /dev/null 2>&1
	if [ $? != 0 ]; then
		echo "** $cmd not found"
		exit 1
	fi
done

# The downloader, tis-fetch.py, needs the Python requests module
python3 -c "import requests" > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "** Python module requests not found (apt install python3-requests)"
	exit 1
fi

# PDFs: tis-pdfbook.py needs pikepdf, and wkhtmltopdf's "patched qt" build for links inside the PDFs
python3 -c "import pikepdf" > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "** Python module pikepdf not found (apt install python3-pikepdf).  Needed to make PDFs."
	exit 1
fi
wkhtmltopdf -V 2>/dev/null | grep -q "patched qt"
if [ $? != 0 ]; then
	echo "** Warning: wkhtmltopdf is not the \"with patched qt\" build, so links inside PDFs won't work."
	echo "   Get it from https://wkhtmltopdf.org/downloads.html"
fi

echo "Creating folders..."
mkdir -p $TISTMPDIR
mkdir -p $DOWNLOAD_TO
mkdir -p $CONFIG_DIR

if [ -f $CONFIG_DIR/tis-clone.cfg ]; then
	echo "$CONFIG_DIR/tis-clone.cfg already exists, skipping (NOT overwriting)"
else
	echo "Creating a default $CONFIG_DIR/tis-clone.cfg file"
	# Give this install its own siid (see SIID in tis-clone.cfg and issue #11)
	SIID=1`LC_ALL=C tr -dc 0-9 < /dev/urandom | head -c 12`
	sed -e "s/^SIID=.*/SIID=${SIID}/" $FOLDER/tis-clone.cfg > $CONFIG_DIR/tis-clone.cfg
fi
