#!/bin/sh
#
# Convert HTML pages to PDFs and Consolidate PDFs into one location
#

. /etc/tis-clone.cfg

###
### Globals
###
GS="gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH"

###
### Consolidate PDFs for the Body Repair Manual
###
doBRM() {
  if [ -d ${URL}/brm/contents ]; then
	cd ${URL}/brm/contents
	for f in `ls *.html | cut -d. -f1`; do
		wkhtmltopdf ${f}.html ${f}.pdf
	done

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep INTRODUCTION|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/BodyRepair-Introduction.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "BODY WELD POINT"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/BodyRepair-BodyWeldPoint.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "BODY DIMENSIONS"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/BodyRepair-BodyDimensions.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "PAINTING / COATING"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/BodyRepair-PaintCoating.pdf $FILES
	cd -

  elif [ -d ${URL}/brm/pdf ]; then
	${GS} -sOutputFile=${URL}/PDFs/BodyRepair-BodyDimensions.pdf ${URL}/brm/pdf/m_di*
	${GS} -sOutputFile=${URL}/PDFs/BodyRepair-BodyPanelReplacement.pdf ${URL}/brm/pdf/m_bp*
	${GS} -sOutputFile=${URL}/PDFs/BodyRepair-Introduction.pdf ${URL}/brm/pdf/m_in*
	${GS} -sOutputFile=${URL}/PDFs/BodyRepair-PaintCoating.pdf ${URL}/brm/pdf/m_pc*
  fi
  return
}

###
### Consolidate PDFs for the New Car Features
###
doNCF() {
  if [ -d ${URL}/ncf/contents ]; then
	cd ${URL}/ncf/contents
	for f in `ls *.html | cut -d. -f1`; do
		wkhtmltopdf ${f}.html ${f}.pdf
	done

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "NEW MODEL OUTLINE"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-NewModelOutline.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "ENGINE"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-Engine.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "CHASSIS"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-Chassis.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep 'BODY<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-Body.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "BODY ELECTRICAL"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-BodyElectrical.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "APPENDIX"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-Appendix.pdf $FILES

	FILES=`cat ../control/toc.xml |sed -e 's/section/\n/g'|grep "NEW FEATURES"|sed -e 's/para id="/\n/g'|cut -d\" -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
	${GS} -sOutputFile=../../PDFs/NewCarFeatures-Updates.pdf $FILES
	cd -

  elif [ -d ${URL}/ncf/pdf ]; then
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-Appendix.pdf ${URL}/ncf/pdf/*/m_ap*
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-BodyElectrical.pdf ${URL}/ncf/pdf/*/m_be*
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-Body.pdf ${URL}/ncf/pdf/*/m_bo*
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-Chassis.pdf ${URL}/ncf/pdf/*/m_ch*
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-Engine.pdf ${URL}/ncf/pdf/*/m_eg*
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-NewModelOutline.pdf ${URL}/ncf/pdf/*/m_mo*
	${GS} -sOutputFile=${URL}/PDFs/NewCarFeatures-Updates.pdf ${URL}/ncf/pdf/*/m_0*
  fi
  return
}

###
### Copy Service Data Sheet into Consolidated PDF folder
###
doSDS() {
  if [ -d ${URL}/sds ]; then
	cp ${URL}/sds/sds.pdf ${URL}/PDFs/ServiceDataSheet-ServiceDataSheet.pdf
  elif [ -d ${URL}/repair/pdf ]; then
	${GS} -sOutputFile=${URL}/PDFs/ServiceDataSheet-ServiceDataSheet.pdf ${URL}/repair/pdf/*.pdf 
  fi
  return
}

###
### Figure out Wiring Diagram folder structure
###
doEWD() {
  if [ -d ${URL}/ewd/manual/ewd/contents/ ]; then
  	EWD=${URL}/ewd/manual/ewd/contents
  elif [ -d ${URL}/ewd/ewd/contents ]; then
	EWD=${URL}/ewd/ewd/contents
  elif [ -d ${URL}/ewd/Overall ]; then
	EWD=${URL}/ewd
  elif [ -d ${URL}/ewd/overall ]; then
	EWD=${URL}/ewd
  else
	EWD=/bogus
  fi

  ###
  ### Consolidate PDFs for the Wiring Diagrams
  ###
  if [ -d ${EWD} ]; then
	if [ -d ${EWD}/overall ]; then
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-Overall.pdf ${EWD}/overall/pdf/*.pdf
	else
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-Overall.pdf ${EWD}/Overall/pdf/*.pdf
	fi

	if [ -d ${EWD}/relay ]; then
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-Relay.pdf ${EWD}/relay/pdf/*.pdf
	else
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-Relay.pdf ${EWD}/Relay/pdf/*.pdf
	fi

	if [ -d ${EWD}/routing ]; then
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-Routing.pdf ${EWD}/routing/pdf/*.pdf
	else
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-Routing.pdf ${EWD}/Routing/pdf/*.pdf
	fi

	if [ -d ${EWD}/system ]; then
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-System.pdf ${EWD}/system/pdf/*.pdf
	else
		${GS} -sOutputFile=${URL}/PDFs/ElectricalWiringDiagram-System.pdf ${EWD}/System/pdf/*.pdf
	fi
  fi
  return
}

###
### Figure out Repair Manual folder structure
###
doRM() {
	if [ -d ${URL}/rm/document/rm/RM0800U/xhtml/ ]; then
		RMAN=${URL}/rm/document/rm/RM0800U/xhtml/
	elif [ -d ${URL}/repair2/html/contents/ ]; then
		RMAN=${URL}/repair2/html/contents/
	elif [ -d ${URL}/repair/contents/ ]; then
		RMAN=${URL}/repair/contents/
	else
    	echo "Cannot find repair manual HTML files"
		exit 1
	fi
	cd $RMAN
	for f in `ls *.html | cut -d. -f1`; do
		wkhtmltopdf ${f}.html ${f}.pdf
	done

	###
	### For the older style GSIC, try to determine the Repair Manual categories
	###
	if [ -d {$URL}/repair2/html/toc ]; then
		cd ${URL}/repair2/html/toc
		for f in `ls sts_*|sed -e 's/sts_//g'|sed -e 's/.html//g'`
		do 
			title=`grep body sts_${f}.html | sed -e 's/<\/.*>//g' | sed -e 's/<.*>//g' | sed -e 's/^\s*//g' | sed -e 's:/::g' | sed -e 's/ //g'`
			files=`cat ${f}.html |sed -e 's/frame_rm/\nrm/g'|sed -e 's/\.html.*$/.pdf/g'|grep -v \<|xargs`
			cd ../contents/
			${GS} -sOutputFile=${URL}/PDFs/RepairManual-${title}.pdf ${files}
			cd ../toc/
		done
	###
	### For the newer style TIS site determine the Repair Manual categories this way
	###
	elif [ -d ${URL}/rm/resources/jsp/siviewer ]; then
		SECTIONS=`ls rm/resources/jsp/siviewer/nav.jsp\@locale\=en\&dir\=rm_252FRM0800U\&section\=*|awk -F= '{print $NF}'|xargs`
		for SECTION in $SECTIONS; do
			title=`echo $SECTION | sed -e 's/+//g' | sed -e 's/_252F//g'`;
			${GS} -sOutputFile=${URL}/PDFs/RepairManual-${title}.pdf `cat ${URL}/rm/resources/jsp/siviewer/nav.jsp\@locale\=en\&dir\=rm_252FRM0800U\&section\=${SECTION} \
				| grep "var TREE_ITEMS" \
				| sed -e 's/,/\n/g' \
				| sed -e "s/'//g" \
				| grep '/xhtml/' \
				| sed -e 's;../../../;rm/;g' \
				| sed -e 's/.html$/.pdf/g' \
				| xargs`  
		done
	###
	### Last ditch effort - Make assumptions and try this GSIC style
	###
	else
		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>General<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-General.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Engine / Hybrid System<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-EngineHybridSystem.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Drivetrain<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-Drivetrain.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Suspension<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-Suspension.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Brake<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-Brake.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Steering<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-Steering.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Audio / Visual / Telematics<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-AudioVisualTelematics.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Power Source / Network<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-PowerSourceNetwork.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Vehicle Interior<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-VehicleInterior.pdf $FILES

		FILES=`cat ../control/toc.xml |sed -e 's/servcat/\n/g'|grep 'name>Vehicle Exterior<'|sed -e 's/para id="/\n/g'|cut -d\" -f1|cut -d_ -f1|sed -e 's/$/.pdf/g'|grep -v id=|xargs`; 
		${GS} -sOutputFile=../../PDFs/RepairManual-VehicleExterior.pdf $FILES

	fi
	cd -
	return
}

###
### Create index.html
###
makeIndex() {
	cd ${URL}/PDFs/
	echo "<title>Consolidated PDFs</title><h1>Consolidated PDFs</h1>" > index.html
	for category in `ls *.pdf|sed -e 's/.pdf//g'|cut -d- -f1|sort -u`
	do 
		echo "<h3>$category</h3><ul>" >> index.html
		for file in `ls $category-*|sed -e 's/.pdf//g'|cut -d- -f2`
		do
			orig=`stat -c %s $category-$file.pdf`
			size=`expr $orig / 1024 / 1024`
			echo "<li><a href='$category-$file.pdf'>$file</a> ($size MB)</li>" >> index.html
		done
		echo "</ul>" >> index.html
	done
	cd - > /dev/null 2>&1
	return
}


###
### Figure out folder to work in
###
if [ x${1} = x ]; then 
	echo "Syntax: $0 <folder>"
	echo "   i.e. $0 ./rm0800u"
	echo "   to run from the current folder, use '$0 .'"
	exit 1
fi
URL=$1

mkdir -p ${URL}/PDFs

doBRM
doNCF
doSDS
doEWD
doRM
makeIndex

exit

