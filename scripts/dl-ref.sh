#!/bin/sh
#
# Download a vehicle's Reference Information: owner's, navigation and accessory manuals, the warranty and
# maintenance guide, the older Flat Rate Manuals, dealer model reference, VIN decoder chart, emergency
# response guides, ...
#
# tis-refsearch.py searches TIS for them and writes the list as a toc.xml in
# $FSM_URLBASE/t3Portal/external/en/ref/DIVISION_MODEL_YEAR/, then dl-html-inc.sh downloads every document
# and makes the navigation page, so it shows up on the front page like the other manuals.  Rerunning it
# searches again (picking up new documents) and resumes the download.
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

if [ $# != 3 ]; then
	echo "Syntax: $0 DIVISION MODEL YEAR"
	echo "    ie: $0 LEXUS LX600 2024"
	echo "        $0 TOYOTA \"Land Cruiser\" 2013-2015"
	echo "    YEAR can be a range.  ${SCRIPT_BASE}/tis-refsearch.py --models DIVISION lists the models."
	exit 1
fi

NAME=`echo "$1_$2_$3" | tr 'a-z /' 'A-Z__'`
FOLDER=/t3Portal/external/en/ref/${NAME}
mkdir -p ${FSM_URLBASE}${FOLDER}

${SCRIPT_BASE}/tis-refsearch.py --toc ${FSM_URLBASE}${FOLDER}/toc.xml "$1" "$2" "$3"
RC=$?
[ $RC = 75 ] && exit 75
if ! grep -q 'href="/' ${FSM_URLBASE}${FOLDER}/toc.xml 2>/dev/null; then
	echo "TIS found no Reference Information documents for $1 $2 $3"
	exit ${RC}
fi

${SCRIPT_BASE}/dl-html-inc.sh ${FOLDER}
RC2=$?
[ $RC2 = 0 ] || exit $RC2
# A search that failed (RC 1) means some documents may be missing from the list; rerunning tries again
exit ${RC}
