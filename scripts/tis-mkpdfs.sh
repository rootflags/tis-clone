#!/bin/sh
#
# Generate consolidated PDFs from HTML files for newer TIS structure
#

. ${HOME}/.tis/tis-clone.cfg
. ${SCRIPT_BASE}/tis-log.sh

GS="gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH"

cd ${FSM_URLBASE}
echo "Running from $FSM_URLBASE"

ls -d t3Portal > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "No t3Portal folder found.  Check FSM_URLBASE in ${HOME}/.tis/tis-clone.cfg"
	exit 1
fi

if [ x$1 = x ]; then
	echo "Syntax: $0 [GSIC_CODE]"
	echo "    ie: $0 27J0U"
	exit 1
fi


GSICCODE=$1
PDFDIR=${FSM_URLBASE}/PDFs
mkdir -p $PDFDIR

MODEL=""

# Repair, Body/Collision Repair and New Car Features manuals (and older PDF manuals with a toc.xml): one PDF
# per manual, with working links and bookmarks.  See tis-pdfbook.py.
FAILED=0
for XHTML in `find . -type d -name xhtml|grep 'document.*/xhtml$'|grep ${GSICCODE}`
do
	TOC=`echo $XHTML|sed -e 's/xhtml$/toc.xml/g'|sed -e 's:/document/:/external/en/:g'`
	[ -f ${TOC} ] || continue
	DOCID=`basename \`dirname ${TOC}\``
	case ${DOCID} in
		RM*) TYPE=RepairManual ;;
		NM*|NCF*) TYPE=NewCarFeatures ;;
		BM*|CR*) TYPE=CollisionRepair ;;
		BR*) TYPE=BodyRepair ;;
		EM*|EWD*|WD*) TYPE=ElectricalWiringDiagram ;;
		*) TYPE=Manual ;;
	esac
	if [ x"${MODEL}" = x ]; then
		MODEL=`${SCRIPT_BASE}/toc2topic ${TOC}`
		mkdir -p "${PDFDIR}/${MODEL}"
	fi
	echo "* Making ${PDFDIR}/${MODEL}/${TYPE}-${DOCID}.pdf"
	${SCRIPT_BASE}/tis-pdfbook.py ${TOC} "${PDFDIR}/${MODEL}/${TYPE}-${DOCID}.pdf" || FAILED=1
done

# *** EVERYTHING BELOW HERE NEEDS WORK
###
### Figure out Wiring Diagram folder structure
###
# *** DIR PATH IS BROKEN, NEED TO ADJUST FRO M$XHTML *** #$
for XHTML in `find . -type d -name xhtml|grep 'external.*/xhtml$'|grep ${GSICCODE}`
do
	EWD_BASE=`echo ${FSM_URLBASE}/${XHTML}|sed -e 's:/xhtml$::g'`
	#if [ -d t3Portal/external/en/ewdappu/EM${GSICCODE}/ewd/contents ]; then
	if [ -d $EWD_BASE/ewd/contents ]; then
		EWD=$EWD_BASE/ewd/contents
	else
		echo "Cannot locate Wiring Diagrams at $EWD_BASE/ewd/contents"
		exit
	fi

	###
	### Consolidate PDFs for the Wiring Diagrams
	###
	echo "Compiling Wiring Diagrams for EM${GSICCODE}"
	if [ x"${MODEL}" = x ]; then
		MODEL=`${SCRIPT_BASE}/toc2topic $EWD_BASE/xhtml/termdata.xml`
		mkdir -p "${PDFDIR}/${MODEL}"
	fi
	echo "* Overall PDFs"
	if [ -d ${EWD}/overall ]; then
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Overall.pdf ${EWD}/overall/pdf/*.pdf
	else
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Overall.pdf ${EWD}/Overall/pdf/*.pdf
	fi

	echo "* Relay PDFs"
	if [ -d ${EWD}/relay ]; then
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Relay.pdf ${EWD}/relay/pdf/*.pdf
	else
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Relay.pdf ${EWD}/Relay/pdf/*.pdf
	fi

	echo "* Routing PDFs"
	if [ -d ${EWD}/routing ]; then
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Routing.pdf ${EWD}/routing/pdf/*.pdf
	else
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Routing.pdf ${EWD}/Routing/pdf/*.pdf
	fi

	echo "* System PDFs"
	if [ -d ${EWD}/system ]; then
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-System.pdf ${EWD}/system/pdf/*.pdf
	else
		${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-System.pdf ${EWD}/System/pdf/*.pdf
	fi
done

# Regenerate PDF index file(s)

exit ${FAILED}
