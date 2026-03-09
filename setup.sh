#!/bin/sh
#
# Initial setup script
#


echo -n "Loading tis-clone.cfg defaults "
if [ -f ${HOME}/.tis/tis-clone.cfg ]; then
	echo "from $HOME/.tis/tis-clone.cfg"
	. ${HOME}/.tis/tis-clone.cfg
else 
	FOLDER=`dirname $0`
	echo "from $FOLDER/tis-clone.cfg "
	. ./$FOLDER/tis-clone.cfg
fi

echo "Creating folders..."
mkdir -p $TISTMPDIR
mkdir -p $DOWNLOAD_TO
mkdir -p $CONFIG_DIR
mkdir -p $MYURL_BASE
if [ $? != 0 ]; then
	echo "** No permission to create $MYURL_BASE.  Create and set ownership to $USER before proceeding **"
fi

if [ -f $CONFIG_DIR/tis-clone.cfg ]; then
	echo "$CONFIG_DIR/tis-clone.cfg already exists, skipping (NOT overwriting)"
else
	echo "Creating a default $CONFIG_DIR/tis-clone.cfg file"
	cp tis-clone.cfg $CONFIG_DIR
fi
