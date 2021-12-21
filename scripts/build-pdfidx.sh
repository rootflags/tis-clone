#!/bin/sh
#
# Create index.html for PDFs
#

. /etc/tis-clone.cfg

echo '<!DOCTYPE html><html><head><title>PDF Files</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <link rel="stylesheet" href="/framework/bootstrap.min.css">
  </head>
  <body style="padding:0px; margin:0px;">
  <img src="/t3Portal/resources/images/globals/header/headerbar.bg.blu.gif" style="width:100%; height:40px; margin:0px; border:0px; padding:0px">
  <ul class="nav flex-column flex-nowrap">';

cd ${FSM_URLBASE}
sub1=0
find PDFs -mindepth 1 -maxdepth 1 -type d | sort | while read -r FOLDER
do
	sub1=`expr $sub1 + 1`;
	TITLE=`echo ${FOLDER} | sed -e 's;PDFs/;;g'`
	echo "    <li class='nav-item drop'>\n";
        echo "    <a class='nav-link collapsed' href='#submenu${sub1}' data-toggle='collapse' >+ ${TITLE}</a>\n";
	echo "    <div class='collapse' id='submenu${sub1}' aria-expanded='false'>\n";
        echo "    <ul class='flex-column nav' style='padding:0px 0px 0px 40px;'>\n";
	cd "${FOLDER}"
	MODEL=`echo ${FOLDER} | sed -e 's;^PDFs/;;g'`
	for PDF in `ls -1`; do
		FOLDER_URL=`echo ${FOLDER} | sed -e 's/ /\%20/g;'`
		echo "      <li class='nav-item'><a class='nav-link py-0' href='/${FOLDER_URL}/${PDF}' data-toggle='collapse' target="new"><i class="fa fa-fw fa-clock-o"></i>- ${PDF}</a></li>\n";
	done
	echo "    </ul></div>\n";
	cd - > /dev/null 2>&1
done
echo '</ul>
<script src="/framework/jquery-3.4.1.min.js"></script>
<script src="/framework/popper.min.js"></script>
<script src="/framework/bootstrap.min.js"></script>
</body>';

