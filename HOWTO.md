# How to Use the Scripts
1. Checkout this software, ie: into $HOME/tis-clone.  If you put it somewhere else, setup.sh sets $BASE in your tis-clone.cfg to match
   
      ```git clone https://github.com/rootflags/tis-clone ~/tis-clone```
   
2. Run the setup script.  The first time, it creates your settings file, ~/.tis/tis-clone.cfg, from the one in the repo and asks for the settings you're likely to change: where to download to (use a separate folder for each vehicle); optionally your TIS login and 2FA method, so you don't have to type them each time; and, if you publish the download on a website, its address (MYURL, where links in a PDF to another manual go) and folder (MYURL_BASE, only used by the older PDF scripts).  Then it checks the software tis-clone needs and creates the folders.  Run it again any time to review your settings; Enter keeps each current value and "-" clears it.  The other settings are described in the file itself.

      ```cd ~/tis-clone && ./setup.sh```

3. Account Prep:
* Visit TIS (https://techinfo.toyota.com), create an account, and follow the instructions to create an active subscription.  Typically a 2 day subscription will be enough
* Run ```~/tis-clone/scripts/tis-login.sh``` and enter your username and password and which 2FA method you want to use (phone or email)
* Enter the 2FA code.  The script checks the new session by fetching a subscriber-only PDF and only saves $HOME/.tis/cookies.txt if that works, ending with "Login successful!"
* To avoid typing them every time, setup.sh can save your login in ~/.tis/tis-clone.cfg (and keeps that file private, since it then holds your password), or you can add it yourself.  Command line options (`-u USERNAME -p PASSWORD -m 0|1`) override these:

         TIS_USERNAME="you@example.com"
         TIS_PASSWORD="your password"
         TIS_MFA=1          # 0 = email, 1 = text message

* The TIS portal is sometimes slow or drops connections.  If a login fails with "HTTP status: 000" or "could not fetch the test page", wait a while before trying again; each attempt sends another 2FA code.  The page TIS returned is saved in ~/.tis/last-login-portal.html.

4. Download Prep:
* Find the vehicle's identifier with ```~/tis-clone/scripts/tis-lookup.py```.  It asks for the make, model and year (offering only what TIS has, like the website's search page) and prints each manual's code and the command that downloads them, ie: for a 2024 Lexus LX600, `RM3900U`, `EM3900U`, `NM3900U`, `BM3900U` and `tis-clone 3900U`.  You can also give the answers on the command line: `tis-lookup.py TOYOTA "Prius V" 2013` prints `tis-clone 23C0U --bm 18M0U`.
* Or by hand: in the TIS website, search for the vehicle you want (i.e. 2018 Toyota Land Cruiser)
* Determine the Repair Manual (RM), Wiring Diagram (EM or EWD), Body Repair (BM or CR), and New Car Feature (NM or NCF) 5-character identifier.  In this case it's "27J0U" since the folders in the URL have "rm/RM27J0U" or "ewd/EM27J0U".  Note that in some cases the identifier might be different depending on the subsection (i.e. 23C0U is used for the RM, EM, and NM sections for a 2013 Prius V, but 18M0U is the code for the BM section).
* Recent vehicles usually publish the collision repair manual as BM (CR doesn't exist) and New Car Features as NM (NCF doesn't exist).  For example the 2013-2018 RAV4 is RM30B0U, EM30B0U, BM30B0U and NM30B0U.  Trying a type that doesn't exist is harmless: the script stops with "No documents in .../toc.xml" or "termdata.xml did not download".

5. Downloading:
* Files go to the $DOWNLOAD_TO folder in ~/.tis/tis-clone.cfg.  To download another vehicle into its own folder, rerun setup.sh (or edit the file) and change it first.
* **The easy way: one command does steps 4 to 9.**  Run it without an identifier and it asks for the make, model and year (step 4's tis-lookup.py), works out the identifiers, works out which manuals TIS has (RM, EM/EWD/WD, BM/CR/BR, NM/NCF), downloads them, the vehicle's Reference Information (owner's, navigation and accessory manuals, maintenance guide, older Flat Rate Manual, ...; see dl-ref.sh), its Flat Rate Manual labor times (see tis-frm.py) and the website framework, and then, if nothing failed, cleans up the links, builds the front page and makes the PDFs.  Rerun the same command to resume after an interruption or failure.

         ~/tis-clone/tis-clone

  If you already know the identifier you can give it instead.  tis-clone then reads which vehicle it is from the repair manual (ie: "2022-2027 LEXUS LX600 and LX700H"), asks which model (if there are several) and which model year(s) you want the Reference Information for: a year (`2024`), several (`2022,2024`), a range (`2022-2024`) or `all`, or Enter to skip it.  You can also give the answer up front with `--ref MAKE:MODEL:YEAR` (write a space in the model as `_`; tis-lookup.py prints the whole command), and `--no-ref` skips it.  The Flat Rate Manual is saved for the same years; `--no-frm` skips just that:

         ~/tis-clone/tis-clone $IDENTIFIER
         ~/tis-clone/tis-clone 18X0U --bm 0800U --ref TOYOTA:Land_Cruiser:2013

  When a section uses a different identifier, give it separately; the main identifier covers the rest.  Without a main identifier, only the sections you name are downloaded:

         ~/tis-clone/tis-clone 23C0U --bm 18M0U            # 2013 Prius V
         ~/tis-clone/tis-clone --rm 30B0U --bm 30B0U       # only the repair and body/collision manuals
         ~/tis-clone/tis-clone 30B0U --no-pdf              # skip the (slow) PDFs; the website doesn't need them

  **If it stops** (the login keeps failing so you try again later, you press Ctrl-C, the computer restarts, ...), carry on with:

         ~/tis-clone/tis-clone --resume

  It reruns your last command (saved in `$DOWNLOAD_TO/tis-clone.resume`), skips the manuals and PDFs that already finished, and continues the rest without downloading files again.  It only asks you to log in once there's something left to download.  It also rechecks the last files downloaded before the stop, in case the computer went down while saving them, and downloads any bad ones again.

  The rest of steps 5 to 9 describe what it runs, if you'd rather do it by hand.
* cd into the download folder and run the downloader for each manual type, using the identifier above:

         . ~/.tis/tis-clone.cfg
         cd $DOWNLOAD_TO
         ~/tis-clone/scripts/dl-html-rm.sh $IDENTIFIER      # Repair Manual
         ~/tis-clone/scripts/dl-html-ewd.sh $IDENTIFIER     # Electrical Wiring Diagrams
         ~/tis-clone/scripts/dl-html-bm.sh $IDENTIFIER      # Body/Collision Repair (BM)
         ~/tis-clone/scripts/dl-html-cr.sh $IDENTIFIER      # Collision Repair (CR), older vehicles
         ~/tis-clone/scripts/dl-html-nm.sh $IDENTIFIER      # New Car Features (NM)
         ~/tis-clone/scripts/dl-html-ncf.sh $IDENTIFIER     # New Car Features (NCF), older vehicles

  If the identifiers are different per section just run the relevant ones.  This can happen when multiple model years share some but not all docs.  For older (roughly 1990-2000) vehicles whose manuals are PDFs, use the matching `dl-pdf-*.sh` scripts instead; they work the same way.
* Downloads take a while (the RAV4 repair manual is about 12,000 files and 2.5 hours, the wiring diagrams a few hours more).  Run them in `screen` or `tmux` and keep the terminal handy:
  * TIS ends a session after about 5 hours.  The downloader notices and pauses, beeps, and waits for you: nothing is sent while you're away.  When you're back, press Enter; it checks TIS is answering, runs tis-login.sh to send you a 2FA code, and carries on where it stopped once you type it in.  If the login doesn't work you're asked again.  Type q at the prompt to stop instead (rerun the same command later to resume).
  * Everything the scripts print is also appended to `$DOWNLOAD_TO/tis-clone.log` (set `TIS_LOG` in tis-clone.cfg to use another file).  Each run is marked with a `===== date start: command` line and a `===== date exit STATUS: command` line, so `grep '^=====' tis-clone.log` lists every run and how it ended.  The log is only readable by you, since it can include login messages.
  * Progress is kept in `$DOWNLOAD_TO/MANIFEST`, a plain text file with one line per file: `STATUS  PATH  BYTES  TIME  NOTE`.  STATUS is OK, MISSING (404 on TIS), FORBIDDEN (TIS refused it while logged in) or FAILED.  The last line for a path wins.
  * If a download stops (Ctrl-C, network trouble, a login you couldn't finish), just run the same command again.  Files already OK, MISSING or FORBIDDEN are skipped and FAILED ones are retried.  To force a file to download again, delete its lines from MANIFEST.
  * `~/tis-clone/scripts/tis-report.py` reads the MANIFEST and shows, per manual, what's OK, FAILED, FORBIDDEN or MISSING (marking the MISSING files that are normal), any files that have disappeared from disk, recent runs that didn't finish, and the exact commands to download what's left.  Rerunning a script only retries FAILED files; `tis-report.py --retry FORBIDDEN,GONE` marks refused and disappeared files so the next run fetches them too.
  * A script ends with "Some files FAILED" (exit status 1) if anything failed; rerun it.  Exit status 75 means the session expired and it could not log in again: run tis-login.sh, then rerun.
  * Some MISSING files are normal, because TIS itself doesn't have them (e.g. about 120 wiring diagram tree pages per model year, a few icons and intro pages).

6. Download the website framework (the shared TIS scripts, styles and icons the pages use).  It can be run before or after the manuals; rerun it if you download the wiring diagrams again:
* ```~/tis-clone/scripts/dl-framework.sh```

7. Clean up a ton of unneeded links and external website references that won't work locally.  Rerun it after downloading more manuals:
* Run ```~/tis-clone/scripts/tis-urlstripper.sh``` to remove external URLs and remove various garbage that gets created

8. Create PDFs, if you want them:
* ```~/tis-clone/scripts/tis-mkpdfs.sh $IDENTIFIER```
* Each manual (repair, collision, new car features) becomes one PDF in `$DOWNLOAD_TO/techinfo.toyota.com/PDFs/<model>/`, ie: `RepairManual-RM30B0U.pdf`, with the pages in the same order as the website.  Links between pages work inside the PDF on any device (phone, tablet, browser or desktop), and the bookmarks follow the website's navigation.  Links to a different manual go to your website if `MYURL` is set to it, and are left out otherwise.
* It needs wkhtmltopdf's "with patched qt" build (`wkhtmltopdf -V` says so; https://wkhtmltopdf.org/downloads.html) and pikepdf (`apt install python3-pikepdf`).  Pages are rendered several at a time and kept in `$DOWNLOAD_TO/pdfwork`, so it resumes if interrupted; the 2013-2018 RAV4 repair manual (4,500 pages of HTML, 15,000 PDF pages) takes about 5 minutes on 8 cores.
* The wiring diagrams are made into four PDFs (overall, relay, routing, system) from TIS's own diagram PDFs.

9. Create Navigation.  Rerun it after downloading more manuals:
* For HTML docs: ```~/tis-clone/scripts/build-index.py > $DOWNLOAD_TO/techinfo.toyota.com/index.html```

* For PDF docs: ```~/tis-clone/scripts/build-pdfidx.sh > $DOWNLOAD_TO/techinfo.toyota.com/PDFs/index.html```

10. If you have an existing version that you're updating or adding additional vehicles to, merge into existing site.  tis-merge.sh copies the current folder into the target (with rsync, without deleting anything), so run it from the download's techinfo.toyota.com folder:

         cd $DOWNLOAD_TO/techinfo.toyota.com
         ~/tis-clone/scripts/tis-merge.sh /path/to/your/website

    While it's not strictly necessary to copy and merge documents into a different final location than the $DOWNLOAD_TO folder, it is highly recommeneded to do so especially if you have multiple FSMs as it will allow you to update docs in the background rather than having updates (which can include failures) overwriting your live website.

# How to use what you just downloaded
While you can locally browse the "HTML" files you download using your web browser, typical browser security prevents the Javascript used in the website from reading local files off your PC.  Normally that security restriction is a good thing, but in this case it makes displaying the website a challenge as many of the pages will display but the links won't work, or only part of the page will display.

The best way around this problem is to set up a local webserver.  One you have your documents running in the webserver, you can just point your preferred web browser at the location and browse the docs just like you're on the TIS website.  
* The easist way on a Linux desktop is to run the following, and then point your web browser to http://localhost:8080

         ~/tis-clone/scripts/tis-serve.py

  It serves `$FSM_URLBASE` on every network interface (use `-p` for another port, `-b 127.0.0.1` to only allow this computer, or give it a folder).  Plain `python3 -m http.server` isn't enough: it sends the `.jsp` pages as downloads, so the wiring diagrams won't open.
  
* Alternately if you're doing this on a Linux server you could use Apache.  The .jsp pages saved from TIS are plain HTML, so serve them as text/html (otherwise the browser downloads them and the wiring diagrams won't open), and add svgz decompression support to your virtual host:

        AddType text/html jsp
        AddType image/svg+xml svg svgz
        AddEncoding gzip svgz
  
* If you want to run this locally on a Windows or MacOS desktop, then my preferred method is to set up the Abyss webserver.  Instructions for this are available in the [Abyss webserver setup doc](ABYSS.md)
* nginx and other webservers will probably work as well.  Just make sure you can associate JSP files as text/html if the pages don't display correctly as the index.jsp file needs to do some dynamic data loading of XHTML and other file types to create the HTML pages you see.

# Script reference
All scripts are in `~/tis-clone/scripts` and read their settings from `~/.tis/tis-clone.cfg`.  Run the downloaders from `$DOWNLOAD_TO`.  Except for the ones that print a web page (`build-index.py`, `build-pdfidx.sh`, `toc2html.py` and `toc2topic.py`), every script also appends its output to `$DOWNLOAD_TO/tis-clone.log` (see step 5); `tis-log.sh` and `tislog.py` are the shared code that does this.

Everything at once
* `~/tis-clone/tis-clone [CODE] [--rm CODE] [--ewd CODE] [--bm CODE] [--nm CODE] [--ref MAKE:MODEL:YEAR] [--no-ref] [--no-pdf]` - without a CODE, ask for the make, model and year and look the codes up (tis-lookup.py); find which manuals TIS has, download them, the Reference Information (with `--ref`, which the lookup adds) and the framework, then (if nothing failed) run tis-urlstripper.sh, build-index.py and the PDF scripts (step 5).  `tis-clone --resume` carries on with the last command where it stopped.

Logging in
* `tis-login.sh [-u USERNAME] [-p PASSWORD] [-m 0|1]` - log in to TIS (with 2FA) and save the session in ~/.tis/cookies.txt.  Defaults come from TIS_USERNAME, TIS_PASSWORD and TIS_MFA in tis-clone.cfg.
* `confirm-login.sh` - check that the saved session works (exit status 0 if it does, 75 if not).  Same as `tis-fetch.py --check`.

Downloading (HTML manuals, current vehicles)
* `dl-html-rm.sh`, `dl-html-ewd.sh`, `dl-html-bm.sh`, `dl-html-cr.sh`, `dl-html-nm.sh`, `dl-html-ncf.sh` `IDENTIFIER` - download the repair manual, wiring diagrams, body/collision repair and new car features.  They resume where they stopped, log in again when the session expires, and record every file in `$DOWNLOAD_TO/MANIFEST` (see step 5).
* `dl-html-inc.sh URI` - shared by the RM/BM/CR/NM/NCF scripts: downloads every document listed in URI/toc.xml, ie: `dl-html-inc.sh /t3Portal/external/en/cr/BM27J0U`.
* `dl-framework.sh` - download the shared TIS scripts, styles and icons, and patch ewd.js and all-t3.js to work offline.
* `tis-fetch.py [options] URL_OR_PATH ...` or `tis-fetch.py -i FILE` - the downloader all the download scripts use.  It can also fetch individual files by hand, ie: `tis-fetch.py /t3Portal/external/en/rm/RM30B0U/toc.xml`.  Run `tis-fetch.py --help` for the options.

Downloading (older vehicles and odds and ends; these also use tis-fetch.py and the MANIFEST)
* `dl-pdf-rm.sh`, `dl-pdf-ewd.sh`, `dl-pdf-wd.sh`, `dl-pdf-em.sh`, `dl-pdf-bm.sh`, `dl-pdf-br.sh`, `dl-pdf-cr.sh`, `dl-pdf-nm.sh`, `dl-pdf-ncf.sh` `IDENTIFIER` - PDF manuals for roughly 1990-2000 vehicles.  These manuals are a list of small pages that each link to a PDF; the scripts download the pages and the PDFs (including PDFs TIS hides behind a "?locale=" redirect page) and build the manual's navigation page.
* `dl-pdf-any.sh TYPE/IDENTIFIER` - any other PDF section, ie: `dl-pdf-any.sh cr/BR27J0U`.
* `dl-ref.sh DIVISION MODEL YEAR` - download a vehicle's Reference Information, ie: `dl-ref.sh LEXUS LX600 2024` or `dl-ref.sh TOYOTA "Land Cruiser" 2013`.  This is what TIS lists under Library > Reference Information for that vehicle: the owner's, navigation/multimedia and accessory manuals, the warranty and maintenance guide, the older (to about 2015) Flat Rate Manuals, the dealer model reference, VIN decoder chart, fluid specifications, emergency response guides and similar technician references, and ASM/parts reference pages.  YEAR can be a range (`2022-2027`) or a list (`2022,2024-2025`).  It shows up on the front page as "DIVISION YEAR MODEL Reference Information".  Newer vehicles' Flat Rate Manual is a separate TIS application; tis-frm.py saves that.
* `tis-lookup.py [MAKE MODEL YEAR] [--args]` - find a vehicle's manual codes (step 4).  It asks for anything not given.  `--args` prints only the tis-clone arguments, ie: `23C0U --bm 18M0U --ref TOYOTA:Prius_V:2013` (tis-clone uses this when run without a code).  `--ref-for TOC.XML` reads which vehicle a downloaded manual is for, asks for the model year(s) and prints the `--ref` value (tis-clone uses this when given a code without `--ref`).
* `tis-frm.py DIVISION MODEL YEARS` - save a vehicle's Flat Rate Manual (labor times) from TIS's Flat Rate Manual application, ie: `tis-frm.py LEXUS LX600 2024`: every Accessories, Maintenance and Repair operation with its type, operation number and the hours for each VDS (characters 4-8 of the VIN; an empty cell means the operation doesn't apply to that VDS, and "Others" operations ending in `_` have no flat time), plus TIS's General Information PDF.  It shows up on the front page as "DIVISION YEAR MODEL Flat Rate Manual", one page per section.  YEARS takes the same forms as dl-ref.sh.  What it has fetched is kept in `$DOWNLOAD_TO/frmwork/`, so a rerun only fetches what's missing.  `tis-frm.py --pdf DIVISION MODEL YEARS` makes `PDFs/<vehicle>/FlatRateManual-DIVISION_MODEL_YEAR.pdf` from the saved pages (tis-clone does both).
* `tis-refsearch.py DIVISION MODEL YEAR [-g GROUP]` - just list what dl-ref.sh would download.  `tis-refsearch.py --models DIVISION` and `--years DIVISION` list the models and years TIS knows (Toyota's model names are mixed case, ie: `Land Cruiser`; the model is matched without regard to case).
* `dl-anypage.sh URI ...` - download TIS pages plus the images, stylesheets, scripts and PDFs they use, ie: `dl-anypage.sh /t3Portal/index.jsp`.  It does not follow links to other pages.

Checking and cleaning up
* `tis-report.py [-v] [--retry STATUS,...] [--paths STATUS]` - report on the MANIFEST: counts per manual, every FAILED and FORBIDDEN file with the reason, MISSING files by folder (normal ones marked), OK files no longer on disk (GONE), recent runs that didn't finish, and the commands to fix it all.  `--retry FORBIDDEN,MISSING,GONE` marks those for download on the next run; `--paths FAILED` prints just the paths.  Exit status 1 if anything needs downloading.
* `tis-verify.sh [--fix] [-v] [FOLDER]` (or `tis-verify.py`) - check the files on disk: TIS login pages saved in place of pages, images, PDFs and videos (from expired sessions, mostly in downloads made before tis-fetch.py), "PDFs" that are really a redirect page, files that aren't what their name says, empty files, and documents listed in a toc.xml that were never downloaded.  `--last N` checks only the last N files downloaded (tis-clone --resume does this).  `--fix` marks the bad files FAILED in the MANIFEST and the good files it didn't know about OK, so rerunning the download scripts fetches only what's needed; then `tis-report.py` lists the commands.  This is how to repair an old wget download:

         ~/tis-clone/scripts/tis-verify.sh --fix
         ~/tis-clone/scripts/tis-report.py        # then run the commands it lists
* `tis-urlstripper.sh [FOLDER]` - remove absolute TIS links so the copy works on your own web server (step 7).

Building the website and PDFs
* `build-index.py [FOLDER] > index.html` - front page listing every downloaded manual (step 9).
* `tis-serve.py [-p PORT] [-b ADDRESS] [FOLDER]` - serve the download for browsing (see below).  If the port is in use, it uses the next free one.
* `tis-mkpdfs.sh IDENTIFIER` - make the PDFs (step 8), using `tis-pdfbook.py` for each manual and Ghostscript for the wiring diagrams; `build-pdfidx.sh` makes the PDF index page.
* `tis-pdfbook.py TOC.XML OUT.PDF [-j JOBS]` - make one PDF of a manual, with working internal links and bookmarks from its toc.xml.
* `repdf PDF ...` - split and re-merge PDF files.
* `toc2html.py toc.xml > toc.html` - navigation page for one manual (run by the downloaders).
* `toc2topic.py toc.xml` - print the vehicle a manual is for, ie: `TOYOTA 2013-2018 RAV4` (tis-mkpdfs.sh uses it to name the PDF folder).
* `tis-merge.sh TARGET` - copy the current folder into your website (step 10).
* `make-iso.sh` - build an ISO image of the download (written for the Land Cruiser; edit the name and volume label first).
* Older helpers kept for reference, generally not needed anymore: `tis-pdfer.sh`, `tis-html2pdf.sh`, `tis-html2pdf2.sh`, `tis-xhtml2pdf.sh` (the old PDF method, which needed a `/t3Portal` link and couldn't keep links working).
