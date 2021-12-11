#!/bin/sh
#
# Generate consolidated PDFs from HTML files for newer TIS structure
#

export TMPDIR=/data/local/tmp
GS="gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH"

ls -d t3Portal > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "No t3Portal folder found.  You must run this from the parent folder above t3Portal"
	exit 1
fi

if [ x$2 = x ]; then
	echo "Syntax: $0 [GSIC_CODE] [PDF_TARGET]"
	echo "    ie: $0 27J0U TOYOTA/LAND_CRUISER/J200/PDFs"
	exit 1
fi

ls -d $2 > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "PDF folder $2 does not exist"
	exit 1
fi

GSICCODE=$1
PDFDIR=$2

# Body/Collision Repair Manual
if [ -d t3Portal/document/cr/BM${GSICCODE}/xhtml ]; then
	echo "Generating PDFs for BM${GSICCODE}"
	cd t3Portal/document/cr/BM${GSICCODE}/xhtml
	/opt/tis-scripts/tis-xhtml2pdf.sh cr/BM${GSICCODE}
	echo "Consolidating PDFs for BM${GSICCODE}"
	cd ../../../../../
	echo /opt/tis-scripts/toc2pdf t3Portal/external/en/cr/BM${GSICCODE}/toc.xml ${PDFDIR}
	/opt/tis-scripts/toc2pdf t3Portal/external/en/cr/BM${GSICCODE}/toc.xml ${PDFDIR}
	rm -f t3Portal/document/cr/BM${GSICCODE}/xhtml/*.pdf
fi

# New Car Features
if [ -d t3Portal/document/ncf/NM${GSICCODE}/xhtml ]; then
	echo "Generating PDFs for NM${GSICCODE}"
	cd t3Portal/document/ncf/NM${GSICCODE}/xhtml
	/opt/tis-scripts/tis-xhtml2pdf.sh ncf/NM${GSICCODE}
	echo "Consolidating PDFs for NM${GSICCODE}"
	cd ../../../../../
	/opt/tis-scripts/toc2pdf t3Portal/external/en/ncf/NM${GSICCODE}/toc.xml ${PDFDIR}
	rm -f t3Portal/document/ncf/NM${GSICCODE}/xhtml/*.pdf
fi

# Repair Manual
if [ -d t3Portal/document/rm/RM${GSICCODE}/xhtml ]; then
	echo "Generating PDFs for RM${GSICCODE}"
	cd t3Portal/document/rm/RM${GSICCODE}/xhtml
	/opt/tis-scripts/tis-xhtml2pdf.sh rm/RM${GSICCODE}
	echo "Consolidating PDFs for RM${GSICCODE}"
	cd ../../../../../
	/opt/tis-scripts/toc2pdf t3Portal/external/en/rm/RM${GSICCODE}/toc.xml ${PDFDIR}
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
if [ -d ${EWD}/overall ]; then
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-Overall.pdf ${EWD}/overall/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-Overall.pdf ${EWD}/Overall/pdf/*.pdf
fi

if [ -d ${EWD}/relay ]; then
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-Relay.pdf ${EWD}/relay/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-Relay.pdf ${EWD}/Relay/pdf/*.pdf
fi

if [ -d ${EWD}/routing ]; then
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-Routing.pdf ${EWD}/routing/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-Routing.pdf ${EWD}/Routing/pdf/*.pdf
fi

if [ -d ${EWD}/system ]; then
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-System.pdf ${EWD}/system/pdf/*.pdf
else
	${GS} -sOutputFile=${PDFDIR}/ElectricalWiringDiagrams-EM${GSICCODE}-System.pdf ${EWD}/System/pdf/*.pdf
fi
