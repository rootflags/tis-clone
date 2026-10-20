#!/bin/sh
#
# Remove external URLs from the FSM docs so that you don't get broken references
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

FOLDER=$1
if [ x${FOLDER} = x ]; then
	FOLDER=${FSM_URLBASE}
fi

# First, remove duplicate redirect links (wget saved these with the query string in the file name)
echo "Removing duplicate linkage"
find "${FOLDER}" -type f -name '*linkId=*' -print -delete | wc -l | sed -e 's/^ */    removed /' -e 's/$/ files/'

# Then purge any external URLs from the HTML/XML files.  Only files that mention one of the hosts are
# rewritten, in a single perl run.  .orig is included so dl-framework.sh's patched copies stay stripped.
echo "Removing external URLs"
find "${FOLDER}" -type f \( -name '*.xml' -o -name '*.htm' -o -name '*.html' -o -name '*.xsl' -o -name '*.js' \
	-o -name '*.css' -o -name '*.jsp' -o -name '*.orig' \) -print0 | \
	xargs -0 grep -lZE 'techinfo\.(toyota|qa2ddc\.toyota|snapon)\.com' | \
	xargs -0 -r perl -p -i -e '
		BEGIN { $n = @ARGV }
		s;https://techinfo\.toyota\.com:443;;g;
		s;https://techinfo\.toyota\.com;;g;
		s;techinfo\.toyota\.com;;g;
		s;https://techinfo\.qa2ddc\.toyota\.com;;g;
		s;https://techinfo\.snapon\.com;;g;
		END { print STDOUT "    rewrote $n files\n" }'
