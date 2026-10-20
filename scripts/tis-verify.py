#!/usr/bin/env python3
#
# tis-verify.py - Find downloaded files that aren't what they should be
#
# Checks every file under $FSM_URLBASE (or FOLDER, which must be inside it) for the ways a download goes
# wrong, mostly from before tis-fetch.py, when an expired session saved TIS's login page in place of
# documents, images and PDFs:
#   - TIS login pages (the current "Techinfo prelogin" page, the older "TIS is your service support
#     source" one, the "Subscription Level" page) saved as pages, scripts, images or PDFs
#   - "PDFs" that are really the little ?locale= redirect page TIS puts in front of some PDFs
#   - images, PDFs, .svgz and videos whose contents aren't an image, PDF, gzip or video; empty files
#   - documents listed in a toc.xml that were never downloaded
#
# With --fix it records the results in the MANIFEST that tis-fetch.py uses, so rerunning the download
# scripts fetches just what's needed: bad files are marked FAILED (they get downloaded again), and good
# files the MANIFEST doesn't know about yet (ie: from an old wget download) are marked OK (they're
# skipped).  Nothing is deleted; a successful download replaces the bad file.  Then run tis-report.py for
# the commands.
#
# Usage:
#   tis-verify.py [FOLDER]           report
#   tis-verify.py --fix [FOLDER]     report and update the MANIFEST
#   tis-verify.py -v [FOLDER]        list every bad file, not just the first few per folder
#   tis-verify.py --last N [--fix]   only the last N files downloaded (tis-clone --resume uses this)
#
# Exit status: 0 everything looks fine, 1 bad or missing files found.
#

import argparse
import collections
import os
import re
import subprocess
import sys
import time

from tislog import tee_to_log

IMAGE = (b"\x89PNG", b"GIF8", b"\xff\xd8")         # TIS serves some PNGs as .gif/.jpg, so any image will do
MAGIC = {".pdf": (b"%PDF",), ".png": IMAGE, ".gif": IMAGE, ".jpg": IMAGE, ".jpeg": IMAGE, ".svgz": (b"\x1f\x8b",)}
PAGES = {".html", ".htm", ".xhtml", ".jsp", ".xml", ".xsl", ".svg", ".do"}
SCRIPTS = {".js", ".css"}
LOGIN_RE = re.compile(rb"Techinfo prelogin|TIS is your service support source|openam/json/realms|"
                      rb"<title>[^<]*Subscription Level", re.I)
STUB_RE = re.compile(rb"""<script>.*?location\s*=\s*'([^']+)'""", re.S)
HREF_RE = re.compile(r'href="([^"]+\.x?html)[^"]*"')
# Things that aren't downloads: our own files and the website framework copied from the repo
SKIP_DIRS = {"PDFs", "framework"}
SKIP_SUFFIXES = (".orig", ".part", ".bak")


def load_cfg():
    names = ["DOWNLOAD_TO", "FSM_URLBASE", "SCRIPT_BASE", "TIS_LOG"]
    script = '. "$HOME/.tis/tis-clone.cfg" && printf "%s\\0" ' + " ".join('"$%s"' % n for n in names)
    out = subprocess.run(["sh", "-c", script], capture_output=True, check=True).stdout
    return dict(zip(names, out.decode().split("\0")))


def problem(path, size):
    """Why the file at path is bad, or None if it looks fine"""
    ext = os.path.splitext(path.lower())[1]
    if size == 0:
        return None if ext == ".do" else "empty file"      # .do pages are TIS actions that answer with nothing
    with open(path, "rb") as fh:
        head = fh.read(200000 if ext in PAGES or ext in SCRIPTS else 4096)
    if ext in MAGIC:
        if head.startswith(MAGIC[ext]):
            return None
        if LOGIN_RE.search(head):
            return "TIS login page"
        if ext == ".pdf" and STUB_RE.search(head):
            return "redirect page instead of the PDF"
        return "web page instead of a %s file" % ext[1:] if head.lstrip()[:1] == b"<" else "not a %s file" % ext[1:]
    if ext == ".mp4":
        if b"ftyp" in head[:12]:
            return None
        return "web page instead of a video" if head.lstrip()[:1] == b"<" else "not a video"
    if ext in PAGES:
        return "TIS login page" if LOGIN_RE.search(head) else None
    if ext in SCRIPTS:
        # A script or stylesheet that's really an HTML page (all-t3.js mentions the login page in a comment)
        return "TIS login page" if head.lstrip()[:1] == b"<" and LOGIN_RE.search(head) else None
    return None


def manifest_status(path):
    status = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if not line.startswith("#") and "\t" in line:
                    f = line.split("\t")
                    status[f[1]] = f[0]
    return status


def check_last(manifest, status, root, count, fix):
    """Check the files most recently recorded OK, in case the computer stopped while writing them"""
    recent = []
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("OK\t"):
                    recent.append(line.split("\t")[1])
    last = []
    for p in reversed(recent):
        if p not in last and status.get(p) == "OK":
            last.append(p)
            if len(last) == count:
                break
    bad = {}
    for p in last:
        f = os.path.join(root, p.lstrip("/"))
        if p.endswith("/"):
            f = os.path.join(f, "index.html")
        try:
            why = problem(f, os.path.getsize(f))
        except OSError:
            why = "missing"
        if why:
            bad[p] = why
    print("Checked the last %d files downloaded: %s" % (len(last), "all fine" if not bad else "%d bad" % len(bad)))
    for p, why in bad.items():
        print("    %s  (%s)" % (p, why))
    if bad and fix:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(manifest, "a", encoding="utf-8") as fh:
            for p, why in bad.items():
                fh.write("FAILED\t%s\t0\t%s\ttis-verify: %s\n" % (p, stamp, why))
        print("Marked them FAILED, so they're downloaded again.")
    return 1 if bad else 0


def group(path):
    """Folder to report a path under: the manual (ie: /t3Portal/document/rm/RM27J0U) or its parent folder"""
    parts = path.split("/")
    if len(parts) > 5 and parts[2] in ("document", "external"):
        return "/".join(parts[:6] if parts[2] == "external" else parts[:5])
    return "/".join(parts[:-1]) or "/"


def main():
    ap = argparse.ArgumentParser(description="Find downloaded files that aren't what they should be")
    ap.add_argument("folder", nargs="?", help="folder to check (default: $FSM_URLBASE)")
    ap.add_argument("--fix", action="store_true",
                    help="mark bad files FAILED and unknown good files OK in the MANIFEST, so a rerun fetches only what's needed")
    ap.add_argument("--manifest", help="manifest file (default $DOWNLOAD_TO/MANIFEST)")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every bad file")
    ap.add_argument("--last", type=int, metavar="N",
                    help="only check the last N files the MANIFEST lists as OK (what a run was doing when it stopped)")
    args = ap.parse_args()

    cfg = load_cfg()
    tee_to_log(cfg)
    root = os.path.realpath(cfg["FSM_URLBASE"])
    top = os.path.realpath(args.folder or root)
    if top != root and not top.startswith(root + os.sep):
        sys.exit("%s is not inside FSM_URLBASE (%s)" % (top, root))
    manifest = args.manifest or os.path.join(cfg["DOWNLOAD_TO"], "MANIFEST")
    status = manifest_status(manifest)

    if args.last:
        return check_last(manifest, status, root, args.last, args.fix)

    print("Checking files under %s ..." % top, flush=True)
    bad = collections.OrderedDict()
    good_unknown = []
    queries = checked = 0
    for dirpath, dirnames, filenames in os.walk(top):
        if dirpath == root:
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        dirnames.sort()
        for name in sorted(filenames):
            f = os.path.join(dirpath, name)
            if "?" in name:                 # wget saved query-string duplicates; tis-urlstripper.sh removes some
                queries += 1
                continue
            if name.endswith(SKIP_SUFFIXES) or name == "toc.html" or os.path.islink(f):
                continue                    # (toc.html is made by toc2html, not downloaded)
            rel = "/" + os.path.relpath(f, root).replace(os.sep, "/")
            checked += 1
            try:
                why = problem(f, os.path.getsize(f))
            except OSError as e:
                why = "unreadable (%s)" % e.strerror
            if why:
                bad[rel] = why
            elif rel not in status:
                good_unknown.append((rel, os.path.getsize(f)))

    # Documents a toc.xml lists that aren't on disk
    absent = []
    for dirpath, dirnames, filenames in os.walk(top):
        if "toc.xml" in filenames:
            with open(os.path.join(dirpath, "toc.xml"), encoding="utf-8", errors="replace") as fh:
                for href in sorted(set(HREF_RE.findall(fh.read()))):
                    if href.startswith("/") and status.get(href) not in ("MISSING", "FORBIDDEN") and \
                            not os.path.exists(os.path.join(root, href.lstrip("/"))):
                        absent.append(href)

    print("Checked %d files.\n" % checked)
    if bad:
        by_group = collections.OrderedDict()
        for p, why in bad.items():
            by_group.setdefault(group(p), collections.Counter())[why] += 1
        print("Bad files (%d):" % len(bad))
        for g, reasons in by_group.items():
            print("    %-60s %s" % (g, ", ".join("%d %s" % (n, why) for why, n in reasons.most_common())))
        shown = collections.Counter()
        print()
        for p, why in bad.items():
            shown[group(p)] += 1
            if args.verbose or shown[group(p)] <= 3:
                print("    %s  (%s)" % (p, why))
            elif shown[group(p)] == 4:
                print("    ... (-v lists them all)")
    else:
        print("No bad files found.")
    if absent:
        print("\nDocuments listed in a toc.xml but not downloaded (%d):" % len(absent))
        for p in absent if args.verbose else absent[:10]:
            print("    " + p)
        if len(absent) > 10 and not args.verbose:
            print("    ... (-v lists them all)")
    if queries:
        print("\n%d files with a ? in the name (old wget query-string copies) were skipped." % queries)

    if args.fix:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        new = not os.path.exists(manifest)
        with open(manifest, "a", encoding="utf-8") as fh:
            if new:
                fh.write("# tis-fetch.py manifest: STATUS<tab>PATH<tab>BYTES<tab>TIME<tab>NOTE.  Last line per path wins.\n")
            for p, why in bad.items():
                fh.write("FAILED\t%s\t0\t%s\ttis-verify: %s\n" % (p, stamp, why))
            for p, size in good_unknown:
                fh.write("OK\t%s\t%d\t%s\texisting file, checked by tis-verify\n" % (p, size, stamp))
        print("\nUpdated %s: %d bad files marked FAILED, %d good files the MANIFEST didn't know about marked OK."
              % (manifest, len(bad), len(good_unknown)))
        print("Run %s/tis-report.py for the commands that download what's needed." % cfg["SCRIPT_BASE"])
    elif bad or (good_unknown and absent):
        print("\nTo download them again: %s/tis-verify.py --fix%s, then %s/tis-report.py for the commands."
              % (cfg["SCRIPT_BASE"], " " + args.folder if args.folder else "", cfg["SCRIPT_BASE"]))

    return 1 if bad or absent else 0


if __name__ == "__main__":
    sys.exit(main())
