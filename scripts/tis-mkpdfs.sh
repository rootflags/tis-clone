#!/bin/sh
#
# Generate consolidated PDFs from HTML files for newer TIS structure
#
# With SECTIONs (rm, bm, nm, ewd: what tis-clone downloaded), only those manuals of the code; without, all
# of them.  A PDF newer than everything it's made from is skipped (tis-pdfbook.py checks its own).
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
	echo "Syntax: $0 GSIC_CODE [rm] [bm] [nm] [ewd]"
	echo "    ie: $0 27J0U"
	exit 1
fi


GSICCODE=$1
shift
SECTIONS=" $* "
# Is section $1 wanted?
wanted() {
	[ "x${SECTIONS}" = "x  " ] && return 0
	case "${SECTIONS}" in *" $1 "*) return 0 ;; esac
	return 1
}

# Is PDF $1 newer than every file in folder $2?
up_to_date() {
	[ -f "$1" ] && [ -z "`find "$2" -newer "$1" -type f | head -1`" ]
}
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
	case ${DOCID} in
		RM*) S=rm ;;
		NM*|NCF*) S=nm ;;
		BM*|CR*|BR*) S=bm ;;
		EM*|EWD*|WD*) S=ewd ;;
		*) S="" ;;
	esac
	wanted ${S} || continue
	if [ x"${MODEL}" = x ]; then
		MODEL=`${SCRIPT_BASE}/toc2topic.py ${TOC}`
		mkdir -p "${PDFDIR}/${MODEL}"
	fi
	echo "* Making ${PDFDIR}/${MODEL}/${TYPE}-${DOCID}.pdf"
	${SCRIPT_BASE}/tis-pdfbook.py ${TOC} "${PDFDIR}/${MODEL}/${TYPE}-${DOCID}.pdf" || FAILED=1
done

# gs_join folder Name: join contents/folder/pdf/*.pdf (or contents/Name/...) unless already done
gs_join() {
	D=${EWD}/$1
	[ -d ${D} ] || D=${EWD}/$2
	OUT="${PDFDIR}/${MODEL}/ElectricalWiringDiagrams-EM${GSICCODE}-$2.pdf"
	if up_to_date "${OUT}" ${D}/pdf; then
		echo "    up to date, skipping"
	else
		${GS} -sOutputFile="${OUT}.part" ${D}/pdf/*.pdf && mv -f "${OUT}.part" "${OUT}"
	fi
}

# *** EVERYTHING BELOW HERE NEEDS WORK
###
### Figure out Wiring Diagram folder structure
###
# *** DIR PATH IS BROKEN, NEED TO ADJUST FRO M$XHTML *** #$
for XHTML in `find . -type d -name xhtml|grep 'external.*/xhtml$'|grep ${GSICCODE}`
do
	wanted ewd || continue
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
		MODEL=`${SCRIPT_BASE}/toc2topic.py $EWD_BASE/xhtml/termdata.xml`
		mkdir -p "${PDFDIR}/${MODEL}"
	fi
	echo "* Overall PDFs"
	gs_join overall Overall

	echo "* Relay PDFs"
	gs_join relay Relay

	echo "* Routing PDFs"
	gs_join routing Routing

	echo "* System PDFs"
	gs_join system System
done

# Regenerate PDF index file(s)

exit ${FAILED}
