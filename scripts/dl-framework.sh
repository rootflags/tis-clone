#!/bin/sh
#
# Download all of the website framework
#

. /etc/tis-clone.cfg

# Retrieve Wiring Diagram framework
$WG ${WEBSITE}/t3Portal/ewdappu/index.jsp
$WG ${WEBSITE}/t3Portal/external/en/ewdappu/system/js/ewd/EMUtil.js

# Download shared navigation images.  
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/empty.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/page.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/pagesel.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/folder.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/foldersel.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/plus.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/folderopen.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/minus.gif
$WG ${WEBSITE}/t3Portal/resources/images/language/en/english_selected.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/spanish_selected.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/french_selected.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/english_available.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/spanish_available.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/french_available.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/en_unavailable.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/es_unavailable.png
$WG ${WEBSITE}/t3Portal/resources/images/language/en/fr_unavailable.png
$WG ${WEBSITE}/favicon.ico
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/folder.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/empty.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/page.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/pagesel.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/folder.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/plus.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/foldersel.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/folderopen.gif
$WG ${WEBSITE}/t3Portal/resources/jsp/siviewer/icons/minus.gif
$WG ${WEBSITE}/t3Portal/stylegraphics/clear.gif

# Download siviewer, which is the navigation menus.  Then fix the 
${WG} "${WEBSITE}/t3Portal/resources/jsp/siviewer/index.jsp?dir=rm/RM27J0U&href=xhtml/RM100000000SXI0.html&locale=en&model=Land%20Cruiser&MY=2020&t3id=RM100000000SXI0&User=false&publicationNumber=RM27J0U&objType=rm&docid=en_rm_RM27J0U_RM100000000SXI0&context=ti"
for f in `ls -1 ${FSM_URLBASE}/t3Portal/resources/jsp/siviewer/*\?*`; do 
 	NEW=`echo $f | cut -d\? -f1`
	mv "$f" "$NEW"
done

# Strip out external URL calls
FOLDER="${FSM_URLBASE}/t3Portal/resources/jsp/siviewer"
FILES=`find ${FOLDER} -type f|egrep '\.(xml|htm|html|xsl|js|css|jsp)'|cut -d: -f1|sort -u`
for F in $FILES; do
	X=`expr $X + 1`
	echo "Processing $F ($X)"
	perl -p -i -e "s;https://techinfo.toyota.com:443;${MYURL};g" $F
	perl -p -i -e "s;https://techinfo.toyota.com;${MYURL};g" $F
	perl -p -i -e "s;techinfo.toyota.com;${MYURL};g" $F
	perl -p -i -e "s;https://techinfo.qa2ddc.toyota.com;${MYURL};g" $F
	perl -p -i -e "s;https://techinfo.snapon.com;${MYURL};g" $F
done

