#!/bin/sh
#
# Copy a few modified Javascript files into the website tree.  
#

. /etc/tis-clone.cfg

cp ${SCRIPT_BASE}/modified/ewd.js    t3Portal/external/en/ewdappu/system/js/ewd/ewd.js
cp ${SCRIPT_BASE}/modified/all-t3.js t3Portal/framework/skins/t3/js/all-t3.js
cp ${SCRIPT_BASE}/modified/all-t3.js techInfoPortal/framework/skins/t3/js/all-t3.js
