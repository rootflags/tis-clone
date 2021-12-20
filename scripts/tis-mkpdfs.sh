#!/bin/sh
#
# Generate consolidated PDFs from HTML files for newer TIS structure
#

. /etc/tis-clone.cfg

GS="gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH"

cd ${FSM_URLBASE}

ls -d t3Portal > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "No t3Portal folder found.  Check FSM_URLBASE in /etc/tis-clone.cfg"
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

# Body/Collision Repair Manual
if [ -d t3Portal/document/cr/BM${GSICCODE}/xhtml ]; then
	echo "Generating PDFs for BM${GSICCODE}"
	cd t3Portal/document/cr/BM${GSICCODE}/xhtml
	${SCRIPT_BASE}/tis-xhtml2pdf.sh cr/BM${GSICCODE}
	echo "Consolidating PDFs for BM${GSICCODE}"
	cd ../../../../../
	MODEL=`${SCRIPT_BASE}/toc2topic t3Portal/external/en/cr/BM${GSICCODE}/toc.xml`
	mkdir -p "${PDFDIR}/${MODEL}"
	${SCRIPT_BASE}/toc2pdf -x t3Portal/external/en/cr/BM${GSICCODE}/toc.xml -p "${PDFDIR}/${MODEL}"
	rm -f t3Portal/document/cr/BM${GSICCODE}/xhtml/*.pdf
fi

# New Car Features
if [ -d t3Portal/document/ncf/NM${GSICCODE}/xhtml ]; then
	echo "Generating PDFs for NM${GSICCODE}"
	cd t3Portal/document/ncf/NM${GSICCODE}/xhtml
	${SCRIPT_BASE}/tis-xhtml2pdf.sh ncf/NM${GSICCODE}
	echo "Consolidating PDFs for NM${GSICCODE}"
	cd ../../../../../
	if [ x"${MODEL}" = x ]; then
		MODEL=`${SCRIPT_BASE}/toc2topic t3Portal/external/en/cr/BM${GSICCODE}/toc.xml`
		mkdir -p "${PDFDIR}/${MODEL}"
	fi
	${SCRIPT_BASE}/toc2pdf -x t3Portal/external/en/ncf/NM${GSICCODE}/toc.xml -p "${PDFDIR}/${MODEL}"
	rm -f t3Portal/document/ncf/NM${GSICCODE}/xhtml/*.pdf
fi

# Repair Manual
if [ -d t3Portal/document/rm/RM${GSICCODE}/xhtml ]; then
	echo "Generating PDFs for RM${GSICCODE}"
	cd t3Portal/document/rm/RM${GSICCODE}/xhtml
	${SCRIPT_BASE}/tis-xhtml2pdf.sh rm/RM${GSICCODE}
	echo "Consolidating PDFs for RM${GSICCODE}"
	cd ../../../../../
	if [ x"${MODEL}" = x ]; then
		MODEL=`${SCRIPT_BASE}/toc2topic t3Portal/external/en/cr/BM${GSICCODE}/toc.xml`
		mkdir -p "${PDFDIR}/${MODEL}"
	fi
	${SCRIPT_BASE}/toc2pdf -x t3Portal/external/en/rm/RM${GSICCODE}/toc.xml -p "${PDFDIR}/${MODEL}"
	rm -f t3Portal/document/rm/RM${GSICCODE}/xhtml/*.pdf
fi

###
### Figure out Wiring Diagram folder structure
###
if [ -d t3Portal/external/en/ewdappu/EM${GSICCODE}/ewd/contents ]; then
	EWD="t3Portal/external/en/ewdappu/EM${GSICCODE}/ewd/contents"
else
	echo "Cannot locate Wiring Diagrams"
	exit
fi

###
### Consolidate PDFs for the Wiring Diagrams
###
echo "Compiling Wiring Diagrams for EM${GSICCODE}"
if [ x"${MODEL}" = x ]; then
	MODEL=`${SCRIPT_BASE}/toc2topic t3Portal/external/en/ewdappu/EM${GSICCODE}/xhtml/termdata.xml`
	mkdir -p "${PDFDIR}/${MODEL}"
fi
if [ -d ${EWD}/overall ]; then
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Overall.pdf ${EWD}/overall/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Overall.pdf ${EWD}/Overall/pdf/*.pdf
fi

if [ -d ${EWD}/relay ]; then
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Relay.pdf ${EWD}/relay/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Relay.pdf ${EWD}/Relay/pdf/*.pdf
fi

if [ -d ${EWD}/routing ]; then
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Routing.pdf ${EWD}/routing/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-Routing.pdf ${EWD}/Routing/pdf/*.pdf
fi

if [ -d ${EWD}/system ]; then
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-System.pdf ${EWD}/system/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/"${MODEL}"/ElectricalWiringDiagrams-EM${GSICCODE}-System.pdf ${EWD}/System/pdf/*.pdf
fi

# Regenerate PDF index file(s)
