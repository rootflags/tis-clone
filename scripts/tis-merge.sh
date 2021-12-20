#!/bin/sh
#
# Merge any updates into your TIS website
#

. /etc/tis-clone.cfg

if [ x$1 = x ]; then
	echo "This command syncs any new updates into your existing TIS tree"
	echo "syntax: $0 /TARGET/FOLDER"
	exit 0
fi

TARGET=$1

# First, reapply any javascript modifications required
#${SCRIPT_BASE}/tis-rehack.sh
# The above is no longer required with the new website framework

# Then sync the whole thing over
rsync ./ $TARGET/ -a -v --progress                                                                                 
 
