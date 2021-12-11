# tis-clone
Download a copy of the Toyota/Lexus/Scion electronic factory service manual

# Description
This package contains scripts and instructions for you to download your own copy of the Toyota, Lexus, or Scion online Factory Service Manual (FSM).  This tool is designed for personal use by home mechanics who want to work on their vehicle.  This tool has been tested with recent USA versions of the FSM; older documents and non-US FSM versions may not download correctly.

# Requirements
This has been tested on Ubuntu Linux 20.04 LTS but should work on most Linux systems.  It may also function under Cygwin and MacOS but has not been tested.  The following are the base Linux OS requirements:
* /bin/sh (tested with bash)
* Numerous commands which should be part of your Linux distribution: cat, cp, cut, diff, find, grep, head, ls, mkdir, mv, rm, rmdir, sed, sort.  There are likely a few other basic commands I've missed
* wget with SSL support.  "apt install wget".

A recent version of Perl 5 is required.  You will need the following modules:
* Cwd (Included in the Ubuntu libperl5.30 package)
* Data::Dumper (Included in the Ubuntu libperl5.30 package)
* List::MoreUtils (On Ubuntu: apt install liblist-moreutils-perl)
* Switch (On Ubuntu: apt install libswitch-perl)
* XML::Simple (On Ubuntu: apt install libxml-simple-perl)

Other Ubuntu packages which need to be installed:
* Ghostscript (if you want to create PDFs: apt install ghostscript)
* Poppler (pdfinfo, pdfseparate) and pdftk-java (if you want to split the multi-thousand page PDFs into smaller PDFs which are more manageable).  "apt install poppler-utils pkftk-java".
* rsync (if you have an existing download and are updating the documents)
* wkhtmltopdf (required if you want to create PDFs)

# Instructions
Please see the [HOWTO.md](tis-clone/HOWTO.md) file

# License
This tool is freely licensed under the GPL.  If you paid for it, go ask for your money back.  You may download this tool and modify it, however any modifications must also be published and freely licensed under the GPL for others to use. 

This tool is for personal use.  Use of this tool for commercial re-sale purposes is prohibited.  You may NOT resell or republish any files, web pages, or documents this tool downloads.  If you wish to use this tool for commercial re-sale purposes, you must acquire a license from the original author as well as written approval from the owner of the FSM documents.
