#!/bin/sh
#
# Remove external URLs from the FSM docs so that you don't get broken references
#

. /etc/tis-clone.cfg

FOLDER=$1
if [ x${FOLDER} = x ]; then
	FOLDER=${FSM_URLBASE}
fi

# First, remove duplicate redirect links
echo "Removing duplicate linkage"
find ${FOLDER} -name *linkId=* -exec rm -f "{}" \;

# Then purge any external URLs from the HTML/XML files
X=0
FILES=`find ${FOLDER} -type f|egrep '\.(xml|htm|html|xsl|js|css|jsp)'|cut -d: -f1|sort -u`
for F in $FILES; do
	X=`expr $X + 1`
	echo "Processing $F ($X)"
	perl -p -i -e 's;https://techinfo.toyota.com:443;;g' $F
	perl -p -i -e 's;https://techinfo.toyota.com;;g' $F
	perl -p -i -e 's;techinfo.toyota.com;;g' $F
	perl -p -i -e 's;https://techinfo.qa2ddc.toyota.com;;g' $F
	perl -p -i -e 's;https://techinfo.snapon.com;;g' $F
done

