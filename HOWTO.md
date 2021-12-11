# How to Use the Scripts
* Install this software into /tis-clone.  If you put it somewhere else, modify $BASE in tis-clone.cfg with the location
* cp tis-clone.cfg /etc/

Account Prep:
* Get a TIS (techinfo.toyota.com) account, log in via Firefox or Chrome, then view your cookies.  You can do this on any computer you choose - it does not need to be the same one you'll be using to download
* Edit the .cookies.txt and update anything different.  Note that for non-session cookies you'll need to convert the current date plus a few days to the unix epoch date, then update those cookie fields
* Leave your web browser open in the background while downloading so your sessions cookies stay valid

Download Prep:
* Search for the vehicle you want (i.e. 2018 Toyota Land Cruiser)
* Determine the Repair Manual (RM), Wiring Diagram (EM or EWD), Body Repair (BM or CR), and New Car Feature (NM or NCF) identifier.  In this case it's "27J0U" since the folders in the URL have "rm/RM27J0U" or "ewd/EM27J0U"

Downloading:
1. Create a new working directory (i.e. mkdir /working/tis).  If you create a different location you'll need to modify tis-clone.cfg
2. cd into that folder and run all of the downloader scripts using the identifier above:
         cd /working/tis
         for SCRIPT in `ls /tis-clone/scripts/dl-*`; do $SCRIPT $IDENTIFIER; done
   If the identifiers are different per section just run the relevant ones

Clean up:
* Run tis-urlstripper.sh to remove external URLs and remove various garbage that gets created
* Run tis-rehack.sh to apply a few javacsript files which were modified because the originals won't work locally

Create PDFs, if you want them:
* /tis-clone/scripts/tis-mkpdfs.sh

Create Navigation:
This is pretty manual.  It would be great to automate this in a future version
* cd t3Portal/external/en/{ncf,cr,rm}/$IDENTIFIER
* run /tis-clone/scripts/toc2nav toc.xml > /tmp/navarray.txt
* cd /t3Portal/resources/jsp/$IDENTIFIER or create it by copying another folder in the parent directory as a template
* edit nav.jsp, remove "var $TREE_ITEMS = ...", insert /tmp/navarray.txt
* cd TOYOTA/LAND_CRUISER/J200/index_files
* edit nav.html, add new entries


If you have an existing version that you're updating or adding additional vehicles to, merge into existing site:
/tis-clone/scripts/tis-merge.sh

