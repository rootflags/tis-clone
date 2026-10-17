# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A collection of POSIX shell and Perl scripts that mirror the Toyota/Lexus/Scion Factory Service Manual (FSM) from TIS (https://techinfo.toyota.com) for personal offline use, then post-process it into a locally browsable website and optional PDFs. There is no build system, package manager, or test suite. The scripts run against the live site and need an authenticated, paid TIS session. End-user steps are in `HOWTO.md`. Known gaps and wishlist items are in `FUTURE.md`.

## Configuration model (read this first)

Every script starts by sourcing `$HOME/.tis/tis-clone.cfg`, **not** the copy in the repo. `setup.sh` copies `tis-clone.cfg` to `~/.tis/` only if no copy exists there yet. If you change defaults in the repo's `tis-clone.cfg`, existing installs won't pick them up. Key variables:

- `BASE` / `SCRIPT_BASE`: repo location (assumed to be `~/tis-clone`). Scripts call each other through `${SCRIPT_BASE}/...`, so the repo must sit at `$BASE`.
- `DOWNLOAD_TO`: download working directory. wget mirrors into `$DOWNLOAD_TO/techinfo.toyota.com/`, which is `FSM_URLBASE`.
- `WG` (recursive mirror, `-m`) and `WG_NOMIRROR` (`-l 1`): the wget command lines, with a spoofed UA, `-w 0.5`, and both `--load-cookies` and `--save-cookies`. The delay matters: downloading too fast gets the session logged out as a duplicate login. `--save-cookies` matters because TIS rotates session cookies, and a stale cookie file looks like a second login (issue #11).
- `SIID`: the `siid=` value appended to every document request. `setup.sh` writes a random one into a newly created `~/.tis/tis-clone.cfg`.
- `COOKIES` (`~/.tis/cookies.txt`): written by `scripts/tis-login.sh`.
- `TIS_USERNAME` / `TIS_PASSWORD` / `TIS_MFA` (optional, `~/.tis` copy only): defaults for `tis-login.sh`. Its `-u`/`-p`/`-m` flags override them.
- `MYURL_BASE`: local webserver root. `tis-xhtml2pdf.sh` uses it, and may symlink `/t3Portal`, so wkhtmltopdf can resolve absolute web paths.

Perl scripts read config by shelling out, e.g. `` `. $ENV{HOME}/.tis/tis-clone.cfg; echo \$FSM_URLBASE` ``.

## Pipeline / architecture

1. **Auth:** `tis-login.sh` (bash + curl + python3) uses Toyota's OpenAM REST API with email/SMS MFA and writes a Netscape cookie file. `confirm-login.sh` fetches a test PDF. It fails if wget was redirected to `concurrentLoginFailure.html` or the login page, or if the result isn't a real PDF. Every downloader calls it first and stops if it fails. `dl-html-inc.sh` applies the same checks to each fetch.
2. **Download:** documents are keyed by a 5-character GSIC code (e.g. `27J0U`), prefixed per manual type to form TIS paths such as `/t3Portal/external/en/rm/RM27J0U`. Manual types are RM = repair, EM/EWD = wiring, BM/CR = body/collision, NM/NCF = new car features.
   - `dl-html-{rm,bm,cr,nm,ncf}.sh` are thin wrappers that build the folder URI and call `dl-html-inc.sh`. That script fetches `toc.xml`, downloads every `*.xhtml` it references (with a `?sisuffix=…&siid=${SIID}` query string that is then stripped with `mv`), and generates `toc.html` via `toc2html`. It also copies in `website-framework/index.html`.
   - `dl-html-ewd.sh` is the most complex downloader. It probes `EM<code>`, then `EWD<code>`, then the bare `<code>` under `ewdappu/`, starting from `termdata.xml`, and also pulls connector PNG/MP4 assets.
   - `dl-pdf-*.sh` are for older (≈1990–2000) vehicles whose content is PDFs linked from xhtml.
   - `dl-framework.sh` mirrors the shared TIS JS/CSS/JSP viewer framework. `dl-anypage.sh` mirrors an arbitrary URI.
3. **Clean-up:** `tis-urlstripper.sh` deletes `*linkId=*` redirect duplicates and strips absolute TIS hostnames from xml/html/js/css/jsp so the mirror works on localhost.
4. **PDFs (optional):** `tis-mkpdfs.sh <code>` runs `tis-xhtml2pdf.sh` (wkhtmltopdf, run from inside an `xhtml/` dir) per document folder. It then calls `toc2pdf` to consolidate along the toc.xml hierarchy into `FSM_URLBASE/PDFs/<model>/` (ghostscript, pdftk, poppler). The wiring-diagram part of `tis-mkpdfs.sh` is marked as broken/WIP.
5. **Navigation:** `build-index.pl` scans for `toc.html` and EWD `termdata.xml` files and prints a top-level `index.html` to stdout. `build-pdfidx.sh` does the same for PDFs. Both use the Bootstrap/jQuery assets in `website-framework/framework/`.
6. **Publish:** `tis-merge.sh <target>` rsyncs the current directory into a live site tree.

The mirror's `index.jsp` loads XHTML dynamically with JavaScript, so it must be served over HTTP (`python3 -m http.server`, Apache/nginx with `.jsp` mapped to an HTML/JS MIME type, or Abyss per `ABYSS.md`), not opened via `file://`.

## Working on the scripts

- Check dependencies and create directories: `./setup.sh`. It checks for wget (with SSL), gs, poppler, pdftk, rsync, and wkhtmltopdf, plus the Perl modules `List::MoreUtils`, `Switch`, and `XML::Simple`.
- Run one downloader manually: `. ~/.tis/tis-clone.cfg && cd $DOWNLOAD_TO && ~/tis-clone/scripts/dl-html-rm.sh 27J0U`.
- No automated tests. Validate with `sh -n script.sh` / `perl -c script` locally. Real verification needs a logged-in TIS session and hits the live site, so don't run downloaders without the user's go-ahead.
- Style: most scripts are `#!/bin/sh` using backticks, `[ x$1 = x ]` argument checks, and tab indentation. Keep to that. `tis-login.sh` is the exception (bash).
- Most script output still isn't logged (see `FUTURE.md`). Only the session checks above catch a mid-run logout.
- License is GPL; README restricts use to non-commercial personal use.
