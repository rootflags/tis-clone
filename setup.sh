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

echo "Checking dependencies..."
# Confirm we have all the basic packages required
for cmd in cat cp cut diff find grep head ls mkdir mv rm rmdir sed sort wget gs pdfinfo pdfseparate pdftk rsync wkhtmltopdf; do
	which $cmd > /dev/null 2>&1
	if [ $? != 0 ]; then
		echo "** $cmd not found"
		exit 1
	fi
done

# Check for SSL support in wget
ldd `which wget`|grep libssl > /dev/null 2>&1
if [ $? != 0 ]; then
	echo "** wget missing SSL support"
	exit 1
fi

# Check for necessary perl modules
for module in Cwd Data::Dumper Getopt::Long List::MoreUtils Switch XML::Simple; do
	perl -e "use $module;" > /dev/null 2>&1
	if [ $? != 0 ]; then
		echo "** Perl module $module not found"
		exit 1
	fi
done


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
