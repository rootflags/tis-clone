# How to Use the Scripts
1. Check out this software, ie: into $HOME/tis-clone.  If you put it somewhere else, setup.sh sets $BASE in your tis-clone.cfg to match:

         git clone https://github.com/rootflags/tis-clone ~/tis-clone

2. Run the setup script:

         cd ~/tis-clone && ./setup.sh

   The first time, it creates your settings file, ~/.tis/tis-clone.cfg, and asks for:
   * where to download to (use a separate folder for each vehicle);
   * optionally your TIS login and 2FA method, so you don't have to type them each time (the file is then kept private);
   * if you publish the download on a website, its address (MYURL, where links in a PDF to another manual go) and folder (MYURL_BASE, only used by the older PDF scripts).

   Then it checks the software tis-clone needs, shows the command that installs anything missing (apt, dnf, pacman, zypper or Homebrew) and offers to run it.  Run it again any time to review your settings: Enter keeps a value and "-" clears it.

3. Get a TIS subscription and log in:
   * Visit TIS (https://techinfo.toyota.com), create an account and buy a subscription.  A 2 day subscription is usually enough.
   * Run `~/tis-clone/scripts/tis-login.sh`, enter your username, password and 2FA method (phone or email), then the 2FA code.  It ends with "Login successful!"
   * If a login fails with "HTTP status: 000" or "could not fetch the test page", TIS is having a slow moment: wait a while before trying again, since each attempt sends another 2FA code.

4. Download everything with one command:

         ~/tis-clone/tis-clone

   It asks for the make, model and year, then downloads every manual TIS has for it (repair, wiring diagrams, body/collision, new car features), the owner's, navigation and accessory manuals and other Reference Information, the USA service bulletins, tech tips and campaigns/recalls, and the Flat Rate Manual labor times.  Then it builds the website (front page, menus, search) and the PDFs.  Files go to the download folder you chose in step 2; to download another vehicle, rerun setup.sh and change it first.

   * **It takes hours** (the RAV4 repair manual alone is about 12,000 files and 2.5 hours), so run it in `screen` or `tmux`.  TIS ends a session after about 5 hours: the download then pauses and beeps.  When you're back, press Enter, type the 2FA code TIS sends you, and it carries on.
   * **If it stops** (Ctrl-C, a reboot, a login you couldn't finish), carry on where it stopped with:

            ~/tis-clone/tis-clone --resume

   * **If it keeps failing on the same few files** (TIS sometimes sends a file back empty), `--resume` will stop there every time.  This skips them and finishes the website and PDFs anyway:

            ~/tis-clone/tis-clone --continue

   * `~/tis-clone/scripts/tis-report.py` shows what downloaded, what didn't and why.  Some missing files are normal, because TIS doesn't have them either.
   * Everything it prints is also saved in `tis-clone.log` in the download folder.

   Other ways to run it:

         ~/tis-clone/tis-clone 30B0U                       # you already know the code (it asks which model year)
         ~/tis-clone/tis-clone 23C0U --bm 18M0U            # a section with a different code (2013 Prius V)
         ~/tis-clone/tis-clone 18X0U --ref TOYOTA:Land_Cruiser:2013   # give the model year up front
         ~/tis-clone/tis-clone 30B0U --no-pdf              # skip the (slow) PDFs; the website doesn't need them

   When asked for the model year (or with `--ref`) you can give one year (`2024`), several (`2022,2024`), a range (`2022-2024`) or `all`; Enter skips the Reference Information.  `--no-ref` skips the Reference Information, bulletins and Flat Rate Manual; `--no-sb` and `--no-frm` skip just the bulletins or the Flat Rate Manual.  `~/tis-clone/scripts/tis-lookup.py` prints the codes and the full command for a vehicle.

5. Optional: if you keep a website with several vehicles, merge this download into it.  tis-merge.sh copies the download (with rsync, deleting nothing) into your site:

         cd $DOWNLOAD_TO/techinfo.toyota.com
         ~/tis-clone/scripts/tis-merge.sh /path/to/your/website

   Downloading somewhere else and merging, rather than downloading straight into your live site, is recommended: updates (and their failures) then can't break the site while they run.

Then see [How to use what you just downloaded](#how-to-use-what-you-just-downloaded) to browse it.

# Advanced: doing it by hand
Step 4 runs all of this for you.  Use these steps if it doesn't work for a vehicle, or to download or rebuild just one part.

A. Find the vehicle's codes:
* `~/tis-clone/scripts/tis-lookup.py` asks for the make, model and year and prints each manual's 5 character code and the tis-clone command, ie: for a 2024 Lexus LX600, `RM3900U`, `EM3900U`, `NM3900U`, `BM3900U` and `tis-clone 3900U`.  You can give the answers on the command line: `tis-lookup.py TOYOTA "Prius V" 2013` prints `tis-clone 23C0U --bm 18M0U`.
* Or by hand: search for the vehicle on the TIS website and read the code from the manuals' URLs: "rm/RM27J0U" or "ewd/EM27J0U" is code 27J0U.  A section can have a different code (a 2013 Prius V is 23C0U, except its body manual, BM18M0U).
* Manual types: Repair Manual (RM), Wiring Diagrams (EM, EWD or WD), Body/Collision Repair (BM, or CR on older vehicles) and New Car Features (NM, or NCF on older vehicles).  Trying a type that doesn't exist is harmless: the script stops with "No documents in .../toc.xml" or "termdata.xml did not download".

B. Download the manuals.  Run each downloader from the download folder:

         . ~/.tis/tis-clone.cfg
         cd $DOWNLOAD_TO
         ~/tis-clone/scripts/dl-html-rm.sh $IDENTIFIER      # Repair Manual
         ~/tis-clone/scripts/dl-html-ewd.sh $IDENTIFIER     # Electrical Wiring Diagrams
         ~/tis-clone/scripts/dl-html-bm.sh $IDENTIFIER      # Body/Collision Repair (BM)
         ~/tis-clone/scripts/dl-html-cr.sh $IDENTIFIER      # Collision Repair (CR), older vehicles
         ~/tis-clone/scripts/dl-html-nm.sh $IDENTIFIER      # New Car Features (NM)
         ~/tis-clone/scripts/dl-html-ncf.sh $IDENTIFIER     # New Car Features (NCF), older vehicles
         ~/tis-clone/scripts/dl-ref.sh TOYOTA "Prius V" 2013        # Reference Information
         ~/tis-clone/scripts/dl-bulletins.sh TOYOTA "Prius V" 2013  # bulletins, tech tips and campaigns
         ~/tis-clone/scripts/tis-frm.py TOYOTA "Prius V" 2013       # Flat Rate Manual

  For older (roughly 1990-2000) vehicles whose manuals are PDFs, use the matching `dl-pdf-*.sh` scripts instead; they work the same way.
* Progress is kept in `$DOWNLOAD_TO/MANIFEST`, a plain text file with one line per file: `STATUS  PATH  BYTES  TIME  NOTE`.  STATUS is OK, MISSING (404 on TIS), FORBIDDEN (TIS refused it while logged in) or FAILED.  The last line for a path wins.
* If a download stops, run the same command again: files already OK, MISSING or FORBIDDEN are skipped and FAILED ones are retried.  To force a file to download again, delete its lines from MANIFEST.
* A script ends with "Some files FAILED" (exit status 1) if anything failed; rerun it.  Exit status 75 means the session expired and it could not log in again: run tis-login.sh, then rerun.
* `tis-report.py` lists, per manual, what's OK, FAILED, FORBIDDEN or MISSING (marking the MISSING files that are normal, ie: about 120 wiring diagram tree pages per model year), files that have disappeared from disk, and the commands to download what's left.  `tis-report.py --retry FORBIDDEN,GONE` marks refused and disappeared files so the next run fetches them too.
* Each run is marked in `tis-clone.log` with `===== date start: command` and `===== date exit STATUS: command` lines, so `grep '^=====' tis-clone.log` lists every run and how it ended (set `TIS_LOG` in tis-clone.cfg to use another file).

C. Download the website framework (the shared TIS scripts, styles and icons the pages use).  Run it before or after the manuals; rerun it if you download the wiring diagrams again:

         ~/tis-clone/scripts/dl-framework.sh

D. Remove the links to TIS that won't work in your copy.  Rerun it after downloading more manuals:

         ~/tis-clone/scripts/tis-urlstripper.sh

E. Make the PDFs, if you want them:

         ~/tis-clone/scripts/tis-mkpdfs.sh $IDENTIFIER
         ~/tis-clone/scripts/tis-frm.py --pdf TOYOTA "Prius V" 2013   # the Flat Rate Manual

* Each manual (repair, collision, new car features) becomes one PDF in `$DOWNLOAD_TO/techinfo.toyota.com/PDFs/<model>/`, ie: `RepairManual-RM30B0U.pdf`, with the pages in the same order as the website.  Links between pages work inside the PDF on any device (phone, tablet, browser or desktop), and the bookmarks follow the website's navigation.  Links to a different manual go to your website if `MYURL` is set to it, and are left out otherwise.
* It needs wkhtmltopdf's "with patched qt" build (`wkhtmltopdf -V` says so; https://wkhtmltopdf.org/downloads.html) and pikepdf (`apt install python3-pikepdf`).  Pages are rendered several at a time and kept in `$DOWNLOAD_TO/pdfwork`, so it resumes if interrupted; the 2013-2018 RAV4 repair manual (4,500 pages of HTML, 15,000 PDF pages) takes about 5 minutes on 8 cores.
* The wiring diagrams are made into four PDFs (overall, relay, routing, system) from TIS's own diagram PDFs.

F. Build the front page, the search and the PDF index.  Rerun them after downloading more manuals:

         ~/tis-clone/scripts/build-index.py > $DOWNLOAD_TO/techinfo.toyota.com/index.html
         ~/tis-clone/scripts/build-search.py
         cd $DOWNLOAD_TO/techinfo.toyota.com
         for F in $(find t3Portal/external -name toc.html); do ~/tis-clone/scripts/toc2html.py ${F%.html}.xml > $F; done
         ~/tis-clone/scripts/build-pdfidx.sh > $DOWNLOAD_TO/techinfo.toyota.com/PDFs/index.html

* build-search.py makes each manual's search index, and remaking the menus (the `for` line) adds the search box below each manual's menu.  Type a word, a DTC (P0420) or the start of one (P04) and it lists the pages with every word typed under the box: title, section and the text around the match, best matches first.  Click one to open it; the menu closes whatever was open and opens to that page, and both are shown in bold.  Clear the box (or press Esc) to hide the results.  Reference Information, bulletins and the Flat Rate Manual are searched by title.  It all runs in the browser, so it works on any web server, and nothing extra loads until you click the search box.  To take it out again, delete the manuals' `search` folders and remake the menus the same way.

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
All scripts are in `~/tis-clone/scripts` and read their settings from `~/.tis/tis-clone.cfg`.  Run the downloaders from `$DOWNLOAD_TO`.  Except for the ones that print a web page (`build-index.py`, `build-pdfidx.sh`, `toc2html.py` and `toc2topic.py`), every script also appends its output to `$DOWNLOAD_TO/tis-clone.log` (see Advanced B); `tis-log.sh` and `tislog.py` are the shared code that does this.

Everything at once
* `~/tis-clone/tis-clone [CODE] [--rm CODE] [--ewd CODE] [--bm CODE] [--nm CODE] [--ref MAKE:MODEL:YEAR] [--no-ref] [--no-pdf]` - without a CODE, ask for the make, model and year and look the codes up (tis-lookup.py); find which manuals TIS has, download them, the Reference Information (with `--ref`, which the lookup adds) and the framework, then (if nothing failed) run tis-urlstripper.sh, build-index.py, build-search.py and the PDF scripts (step 4).  `tis-clone --resume` carries on with the last command where it stopped.  `tis-clone --continue` does the same without retrying files that failed before, and builds the website and PDFs even if a download failed.

Logging in
* `tis-login.sh [-u USERNAME] [-p PASSWORD] [-m 0|1]` - log in to TIS (with 2FA) and save the session in ~/.tis/cookies.txt.  Defaults come from TIS_USERNAME, TIS_PASSWORD and TIS_MFA in tis-clone.cfg.
* `confirm-login.sh` - check that the saved session works (exit status 0 if it does, 75 if not).  Same as `tis-fetch.py --check`.

Downloading (HTML manuals, current vehicles)
* `dl-html-rm.sh`, `dl-html-ewd.sh`, `dl-html-bm.sh`, `dl-html-cr.sh`, `dl-html-nm.sh`, `dl-html-ncf.sh` `IDENTIFIER` - download the repair manual, wiring diagrams, body/collision repair and new car features.  They resume where they stopped, log in again when the session expires, and record every file in `$DOWNLOAD_TO/MANIFEST` (see Advanced B).
* `dl-html-inc.sh URI` - shared by the RM/BM/CR/NM/NCF scripts: downloads every document listed in URI/toc.xml, ie: `dl-html-inc.sh /t3Portal/external/en/cr/BM27J0U`.
* `dl-framework.sh` - download the shared TIS scripts, styles and icons, and patch ewd.js and all-t3.js to work offline.
* `tis-fetch.py [options] URL_OR_PATH ...` or `tis-fetch.py -i FILE` - the downloader all the download scripts use.  It can also fetch individual files by hand, ie: `tis-fetch.py /t3Portal/external/en/rm/RM30B0U/toc.xml`.  Run `tis-fetch.py --help` for the options.

Downloading (older vehicles and odds and ends; these also use tis-fetch.py and the MANIFEST)
* `dl-pdf-rm.sh`, `dl-pdf-ewd.sh`, `dl-pdf-wd.sh`, `dl-pdf-em.sh`, `dl-pdf-bm.sh`, `dl-pdf-br.sh`, `dl-pdf-cr.sh`, `dl-pdf-nm.sh`, `dl-pdf-ncf.sh` `IDENTIFIER` - PDF manuals for roughly 1990-2000 vehicles.  These manuals are a list of small pages that each link to a PDF; the scripts download the pages and the PDFs (including PDFs TIS hides behind a "?locale=" redirect page) and build the manual's navigation page.
* `dl-pdf-any.sh TYPE/IDENTIFIER` - any other PDF section, ie: `dl-pdf-any.sh cr/BR27J0U`.
* `dl-ref.sh DIVISION MODEL YEAR` - download a vehicle's Reference Information, ie: `dl-ref.sh LEXUS LX600 2024` or `dl-ref.sh TOYOTA "Land Cruiser" 2013`.  This is what TIS lists under Library > Reference Information for that vehicle: the owner's, navigation/multimedia and accessory manuals, the warranty and maintenance guide, the older (to about 2015) Flat Rate Manuals, the dealer model reference, VIN decoder chart, fluid specifications, emergency response guides and similar technician references, and ASM/parts reference pages.  YEAR can be a range (`2022-2027`) or a list (`2022,2024-2025`).  It shows up on the front page as "DIVISION YEAR MODEL Reference Information".  Newer vehicles' Flat Rate Manual is a separate TIS application; tis-frm.py saves that.
* `tis-lookup.py [MAKE MODEL YEAR] [--args]` - find a vehicle's manual codes (Advanced A).  It asks for anything not given.  `--args` prints only the tis-clone arguments, ie: `23C0U --bm 18M0U --ref TOYOTA:Prius_V:2013` (tis-clone uses this when run without a code).  `--ref-for TOC.XML` reads which vehicle a downloaded manual is for, asks for the model year(s) and prints the `--ref` value (tis-clone uses this when given a code without `--ref`).
* `dl-bulletins.sh DIVISION MODEL YEAR` - download a vehicle's USA service bulletins and tech tips (leaving out the ones TIS marks Obsolete) and its service campaigns and safety recalls (dealer letter, technical instructions, ...), ie: `dl-bulletins.sh LEXUS LX600 2024`.  They come from the SB/TT and SC tabs of the TIS Service Information search, and show up on the front page as "DIVISION YEAR MODEL Service Bulletins, Tech Tips and Campaigns", with one section per campaign.  YEAR takes the same forms as dl-ref.sh, and rerunning it picks up new bulletins.  It's `dl-ref.sh --bulletins`.
* `tis-frm.py DIVISION MODEL YEARS` - save a vehicle's Flat Rate Manual (labor times) from TIS's Flat Rate Manual application, ie: `tis-frm.py LEXUS LX600 2024`: every Accessories, Maintenance and Repair operation with its type, operation number and the hours for each VDS (characters 4-8 of the VIN; an empty cell means the operation doesn't apply to that VDS, and "Others" operations ending in `_` have no flat time), plus TIS's General Information PDF.  It shows up on the front page as "DIVISION YEAR MODEL Flat Rate Manual", one page per section.  YEARS takes the same forms as dl-ref.sh.  What it has fetched is kept in `$DOWNLOAD_TO/frmwork/`, so a rerun only fetches what's missing.  `tis-frm.py --pdf DIVISION MODEL YEARS` makes `PDFs/<vehicle>/FlatRateManual-DIVISION_MODEL_YEAR.pdf` from the saved pages (tis-clone does both).
* `tis-refsearch.py DIVISION MODEL YEAR [-g GROUP]` - just list what dl-ref.sh would download (`-g bulletins -g campaigns`: what dl-bulletins.sh would).  `tis-refsearch.py --models DIVISION` and `--years DIVISION` list the models and years TIS knows (Toyota's model names are mixed case, ie: `Land Cruiser`; the model is matched without regard to case).
* `dl-anypage.sh URI ...` - download TIS pages plus the images, stylesheets, scripts and PDFs they use, ie: `dl-anypage.sh /t3Portal/index.jsp`.  It does not follow links to other pages.

Checking and cleaning up
* `tis-report.py [-v] [--retry STATUS,...] [--paths STATUS]` - report on the MANIFEST: counts per manual, every FAILED and FORBIDDEN file with the reason, MISSING files by folder (normal ones marked), OK files no longer on disk (GONE), recent runs that didn't finish, and the commands to fix it all.  `--retry FORBIDDEN,MISSING,GONE` marks those for download on the next run; `--paths FAILED` prints just the paths.  Exit status 1 if anything needs downloading.
* `tis-verify.sh [--fix] [-v] [FOLDER]` (or `tis-verify.py`) - check the files on disk: TIS login pages saved in place of pages, images, PDFs and videos (from expired sessions, mostly in downloads made before tis-fetch.py), "PDFs" that are really a redirect page, files that aren't what their name says, empty files, and documents listed in a toc.xml that were never downloaded.  `--last N` checks only the last N files downloaded (tis-clone --resume does this).  `--fix` marks the bad files FAILED in the MANIFEST and the good files it didn't know about OK, so rerunning the download scripts fetches only what's needed; then `tis-report.py` lists the commands.  This is how to repair an old wget download:

         ~/tis-clone/scripts/tis-verify.sh --fix
         ~/tis-clone/scripts/tis-report.py        # then run the commands it lists
* `tis-urlstripper.sh [FOLDER]` - remove absolute TIS links so the copy works on your own web server (Advanced D).

Building the website and PDFs
* `build-search.py [--force] [FOLDER | toc.xml ...]` - make each manual's search index (`search/` next to its toc.xml) for the search box in its menu (`website-framework/framework/tis-search.js`); manuals whose index is up to date are skipped (Advanced F).
* `build-index.py [FOLDER] > index.html` - front page listing every downloaded manual (Advanced F), plus a Fluid Capacities entry, a page it writes next to it (fluids.html) linking each repair manual's service data pages that give fluid capacities (on newer manuals one MAINTENANCE page per model year range; on older ones the engine cooling and lubrication, transfer, ... pages).
* `tis-serve.py [-p PORT] [-b ADDRESS] [FOLDER]` - serve the download for browsing (see below).  If the port is in use, it uses the next free one.
* `tis-mkpdfs.sh IDENTIFIER [rm] [bm] [nm] [ewd]` - make the PDFs (Advanced E), using `tis-pdfbook.py` for each manual and Ghostscript for the wiring diagrams; `build-pdfidx.sh` makes the PDF index page.  With sections, only those manuals of the code (tis-clone passes the ones it downloaded).  A PDF that's newer than everything it's made from is skipped, so rerunning it only remakes what changed.
* `tis-pdfbook.py TOC.XML OUT.PDF [-j JOBS] [--force]` - make one PDF of a manual, with working internal links and bookmarks from its toc.xml.  It skips an OUT.PDF that's newer than the manual's files, unless `--force`.
* `repdf PDF ...` - split and re-merge PDF files.
* `toc2html.py toc.xml > toc.html` - navigation page for one manual (run by the downloaders).
* `toc2topic.py toc.xml` - print the vehicle a manual is for, ie: `TOYOTA 2013-2018 RAV4` (tis-mkpdfs.sh uses it to name the PDF folder).
* `tis-merge.sh TARGET` - copy the current folder into your website (step 5).
* `make-iso.sh` - build an ISO image of the download (written for the Land Cruiser; edit the name and volume label first).
* Older helpers kept for reference, generally not needed anymore: `tis-pdfer.sh`, `tis-html2pdf.sh`, `tis-html2pdf2.sh`, `tis-xhtml2pdf.sh` (the old PDF method, which needed a `/t3Portal` link and couldn't keep links working).
