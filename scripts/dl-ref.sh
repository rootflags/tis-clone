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
# With --bulletins (or as dl-bulletins.sh) it does the same for the vehicle's USA service bulletins and tech
# tips (without the obsolete ones) and its service campaigns and safety recalls, into
# t3Portal/external/en/bulletins/DIVISION_MODEL_YEAR/, "... Service Bulletins, Tech Tips and Campaigns".
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

KIND=ref
GROUPS=""
WHAT="Reference Information"
RERUN=dl-ref.sh
if [ "x$1" = x--bulletins ]; then
	KIND=bulletins
	GROUPS="-g bulletins -g campaigns"
	WHAT="Service Bulletins, Tech Tips and Campaigns"
	RERUN=dl-bulletins.sh
	shift
fi

if [ $# != 3 ]; then
	echo "Syntax: $0 [--bulletins] DIVISION MODEL YEAR"
	echo "    ie: $0 LEXUS LX600 2024"
	echo "        $0 TOYOTA \"Land Cruiser\" 2013-2015"
	echo "    YEAR can be a range (2022-2024) or a list (2022,2024).  ${SCRIPT_BASE}/tis-refsearch.py --models DIVISION"
	echo "    lists the models."
	exit 1
fi

NAME=`echo "$1_$2_$3" | tr 'a-z /,' 'A-Z__+'`
FOLDER=/t3Portal/external/en/${KIND}/${NAME}
mkdir -p ${FSM_URLBASE}${FOLDER}

${SCRIPT_BASE}/tis-refsearch.py ${GROUPS} --toc ${FSM_URLBASE}${FOLDER}/toc.xml --rerun ${RERUN} \
	--what "${WHAT}" "$1" "$2" "$3"
RC=$?
[ $RC = 75 ] && exit 75
if ! grep -q 'href="/' ${FSM_URLBASE}${FOLDER}/toc.xml 2>/dev/null; then
	echo "TIS found no ${WHAT} documents for $1 $2 $3"
	exit ${RC}
fi

${SCRIPT_BASE}/dl-html-inc.sh ${FOLDER}
RC2=$?
[ $RC2 = 0 ] || exit $RC2
# A search that failed (RC 1) means some documents may be missing from the list; rerunning tries again
exit ${RC}
