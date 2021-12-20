# How to Use the Scripts
1. Install this software into /tis-clone.  If you put it somewhere else, modify $BASE in tis-clone.cfg with the location
* ```mkdir -p /tis-clone && cp -a tis-clone/* /tis-clone/```
* ```cp tis-clone.cfg /etc/```

2. Account Prep:
* Get a TIS (techinfo.toyota.com) account, log in via Firefox or Chrome, then view your cookies.  You can do this on any computer you choose - it does not need to be the same one you'll be using to download
* Edit /tis-clone/cookies.txt and update anything different.  Note that for non-session cookies you'll need to convert the current date plus a few days to the unix epoch date, then update those cookie fields
* Leave your web browser open in the background while downloading so your sessions cookies stay valid

3. Download Prep:
* Search for the vehicle you want (i.e. 2018 Toyota Land Cruiser)
* Determine the Repair Manual (RM), Wiring Diagram (EM or EWD), Body Repair (BM or CR), and New Car Feature (NM or NCF) identifier.  In this case it's "27J0U" since the folders in the URL have "rm/RM27J0U" or "ewd/EM27J0U"

4. Downloading:
* Create a new working directory (i.e. mkdir /working/tis).  If you create a different location you'll need to modify tis-clone.cfg
* cd into that folder and run all of the downloader scripts using the identifier above:

         cd /working/tis
         for SCRIPT in `ls /tis-clone/scripts/dl-*`; do 
                 $SCRIPT $IDENTIFIER
         done

If the identifiers are different per section just run the relevant ones.  This can happen when multiple model years share some but not all docs

5. Clean up a ton of unneeded links and external website references that won't work locally:
* Run ```/tis-clone/scripts/tis-urlstripper.sh``` to remove external URLs and remove various garbage that gets created

6. Create PDFs, if you want them:
* ```/tis-clone/scripts/tis-mkpdfs.sh```

7. Create Navigation:
* For HTML docs: ```/tis-clone/scripts/build-index.pl > /working/tis/techinfo.toyota.com/index.html```

* For PDF docs: ```/tis-clone/scripts/build-pdfidx.sh > /working/tis/techinfo.toyota.com/PDFs/index.html```

8. If you have an existing version that you're updating or adding additional vehicles to, merge into existing site: ```/tis-clone/scripts/tis-merge.sh```

# How to use what you just downloaded
While you can locally browse the "HTML" files you download using your web browser, typical browser security prevents the Javascript used in the website from reading local files off your PC.  Normally that security restriction is a good thing, but in this case it makes displaying the website a challenge as many of the pages will display but the links won't work, or only part of the page will display.

The best way around this problem is to set up a local webserver.  One you have your documents running in the webserver, you can just point your preferred web browser at the location and browse the docs just like you're on the TIS website.  
* If you're doing this on a Linux server you could use Apache.  You may need to add "jsp" to the "application/javascript" line in /etc/mime.types, depending on your installation.
* If you want to run this locally on a Windows or MacOS desktop, then my preferred method is to set up the Abyss webserver.  Instructions for this are available in the [Abyss webserver setup doc](tis-clone/ABYSS.md)
* nginx and other webservers will probably work as well.  Just make sure you can associate JSP files as txt/html if the pages don't display correctly as the index.jsp file needs to do some dynamic data loading of XHTML and other file types to create the HTML pages you see.
