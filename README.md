# tis-clone
Download a copy of the Toyota/Lexus/Scion electronic factory service manual

# Description
This package contains scripts and instructions for you to download your own copy of the Toyota, Lexus, or Scion online Factory Service Manual (FSM).  This tool is designed for personal use by home mechanics who want to work on their vehicle.  This tool has been tested with recent USA versions of the FSM; older documents and non-US FSM versions may not download correctly.

# Requirements
This has been tested on Ubuntu Linux 20.04 LTS but should work on most Linux systems.  It may also function under Cygwin and MacOS but has not been tested.  The following are the base Linux OS requirements:
* /bin/sh (tested with bash)
* Numerous commands which should be part of your Linux distribution: cat, cp, cut, diff, find, grep, head, ls, mkdir, mv, rm, rmdir, sed, sort.  There are likely a few other basic commands I've missed
* curl (used by tis-login.sh).  "apt install curl".
* bash (tis-login.sh), gzip and xargs.
* Python 3 (tis-login.sh, tis-serve.py and the other tools) with the requests module for the downloader, tis-fetch.py.  "apt install python3 python3-requests".  Perl is no longer needed.

Other Ubuntu packages which need to be installed:
* Ghostscript (if you want to create PDFs: apt install ghostscript)
* Poppler (pdfinfo, pdfseparate) and pdftk-java (if you want to split the multi-thousand page PDFs into smaller PDFs which are more manageable).  "apt install poppler-utils pdftk-java".
* rsync (if you have an existing download and are updating the documents)
* wkhtmltopdf, the "with patched qt" build from https://wkhtmltopdf.org/downloads.html, and pikepdf ("apt install python3-pikepdf"), if you want to create PDFs

# Instructions
Please see the [HOWTO.md](HOWTO.md) file.  In short, after setup and logging in, `~/tis-clone/tis-clone` asks for the make, model and year, downloads everything TIS has for that vehicle (or give it an identifier, ie: `~/tis-clone/tis-clone 30B0U`) and builds a local website you can browse with `~/tis-clone/scripts/tis-serve.py`.

# License
This tool is freely licensed under the GPL.  If you paid for it, go ask for your money back.  You may download this tool and modify it, however any modifications must also be published and freely licensed under the GPL for others to use. 

This tool is for personal use.  Use of this tool for commercial re-sale purposes is prohibited.  You may NOT resell or republish any files, web pages, or documents this tool downloads.  If you wish to use this tool for commercial re-sale purposes, you must acquire a license from the original author as well as written approval from the owner of the FSM documents.
