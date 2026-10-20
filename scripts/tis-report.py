#!/usr/bin/env python3
#
# tis-report.py - What failed, and how to fix it
#
# Reads the MANIFEST that tis-fetch.py keeps (default: $DOWNLOAD_TO/MANIFEST) and reports, per manual:
#   - how many files are OK, MISSING (404 on TIS), FORBIDDEN (TIS refused while logged in) and FAILED
#   - every FAILED and FORBIDDEN file with the reason, and MISSING files grouped by folder, with the
#     ones that are normal (TIS doesn't have them either) marked as such
#   - files the MANIFEST says are OK but that are no longer on disk
#   - the commands that download what's left, and recent runs in tis-clone.log that didn't end cleanly
#
# Rerunning a download script retries FAILED files only.  MISSING, FORBIDDEN and vanished files count as
# done, so --retry marks them FAILED in the MANIFEST first (appending lines, nothing is deleted).
#
# Usage:
#   tis-report.py                          report
#   tis-report.py -v                       also list every MISSING file
#   tis-report.py --retry FORBIDDEN,GONE   mark those for download on the next run (GONE = OK but not on disk;
#                                          MISSING works too, though TIS will most likely 404 again)
#   tis-report.py --paths FAILED           just print the paths with that status, one per line
#
# Exit status: 0 nothing left to fix, 1 something FAILED, FORBIDDEN or GONE.
#

import argparse
import collections
import os
import re
import subprocess
import sys
import time

from tislog import tee_to_log

STATUSES = ("OK", "MISSING", "FORBIDDEN", "FAILED")

# Manual folders: /t3Portal/(external/en|document)/<type>/<PREFIX><code>/..., and the wiring diagram viewer
# under ewdappu/<EM|EWD|><code>.  Prefix -> script that downloads that manual.
MANUAL_RE = re.compile(r"^/t3Portal/(?:external/en|document)/(rm|cr|ncf|ewd)/([A-Z]+)([0-9A-Z]{5})/")
EWD_RE = re.compile(r"^/t3Portal/external/en/ewdappu/(EM|EWD|)([0-9A-Z]{5})/")
SCRIPTS = {
    ("rm", "RM"): "dl-html-rm.sh", ("cr", "BM"): "dl-html-bm.sh", ("cr", "CR"): "dl-html-cr.sh",
    ("cr", "BR"): "dl-pdf-br.sh", ("ncf", "NM"): "dl-html-nm.sh", ("ncf", "NCF"): "dl-html-ncf.sh",
    ("ewd", "EM"): "dl-pdf-em.sh", ("ewd", "EWD"): "dl-pdf-ewd.sh", ("ewd", "WD"): "dl-pdf-wd.sh",
}

# MISSING files that are normal: TIS answers 404 for them too, and the viewer copes
NORMAL_MISSING = [
    (re.compile(r"/ewd/contents/tree/\d+/tree-[^/]+\.xml$"), "wiring tree pages TIS doesn't have (the viewer never asks for them)"),
    (re.compile(r"/ewd/icon/zoombar_0[89]\.png$"), "zoom bar icons TIS doesn't have"),
    (re.compile(r"/ewd/intro/(guide|srs_caution)\.html$"), "intro pages this manual doesn't have"),
    (re.compile(r"/ewd/contents/system/compact/[^/]+\.xml$"), "compact diagrams (dl-html-ewd.sh copies the full one)"),
    (re.compile(r"/ewd/contents/connector/figrepair/-\.png$"), "placeholder for connectors with no photo"),
    (re.compile(r"/ewd/styles/css/images/mtrx-bg\.png$"), "background image TIS doesn't have"),
    (re.compile(r"^/favicon\.ico$|^/t3Portal/stylegraphics/(clear|header-left|header-right)\.gif$|"
                r"^/t3Portal/framework/skins/t3/wht3d/images/tab\.bar\.top\.|^/t3Portal/resources/images/tabs/"),
     "framework images TIS doesn't have"),
]


def load_cfg():
    names = ["DOWNLOAD_TO", "FSM_URLBASE", "SCRIPT_BASE", "TIS_LOG"]
    script = '. "$HOME/.tis/tis-clone.cfg" && printf "%s\\0" ' + " ".join('"$%s"' % n for n in names)
    out = subprocess.run(["sh", "-c", script], capture_output=True, check=True).stdout
    return dict(zip(names, out.decode().split("\0")))


def read_manifest(path):
    """Latest (status, bytes, time, note) per path, in first-seen order"""
    entries = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or "\t" not in line:
                continue
            f = line.rstrip("\n").split("\t") + ["", "", "", ""]
            entries[f[1]] = (f[0], f[2], f[3], f[4])
    return entries


def manual_of(path):
    """(label, rerun command) for the manual a path belongs to"""
    m = EWD_RE.match(path)
    if m:
        return "ewdappu/%s%s" % m.groups(), "dl-html-ewd.sh %s" % m.group(2)
    m = MANUAL_RE.match(path)
    if m:
        kind, prefix, code = m.groups()
        script = SCRIPTS.get((kind, prefix), "dl-pdf-any.sh %s/%s" % (kind, prefix))
        if script.startswith("dl-pdf-any.sh"):
            return "%s/%s%s" % (kind, prefix, code), script + code
        return "%s/%s%s" % (kind, prefix, code), "%s %s" % (script, code)
    return "framework and other pages", "dl-framework.sh"


def normal_missing(path):
    if path.endswith("/toc.xml") or path.endswith("/xhtml/termdata.xml"):
        return "this manual doesn't exist on TIS under this code"
    for rx, why in NORMAL_MISSING:
        if rx.search(path):
            return why
    return None


def on_disk(root, path):
    f = os.path.join(root, path.lstrip("/"))
    return os.path.exists(os.path.join(f, "index.html") if path.endswith("/") else f)


def bad_runs(log, count=10):
    """Recent runs in tis-clone.log that exited non-zero: (time, status, command)"""
    if not os.path.exists(log):
        return []
    out = []
    rx = re.compile(r"^===== (\S+ \S+) exit (\S+): (.*)$")
    with open(log, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = rx.match(line)
            # tis-report.py and tis-verify.py exit 1 when they find problems; that's not a failed run
            if m and m.group(2) != "0" and not re.search(r"tis-(report|verify)\.(py|sh)", m.group(3)):
                out.append(m.groups())
    return out[-count:]


def main():
    ap = argparse.ArgumentParser(description="Report what failed in the MANIFEST and how to fix it")
    ap.add_argument("--manifest", help="manifest file (default $DOWNLOAD_TO/MANIFEST)")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every MISSING file, not just a count per folder")
    ap.add_argument("--retry", metavar="STATUS[,STATUS]",
                    help="mark files with these statuses (FORBIDDEN, MISSING, GONE) for download on the next run")
    ap.add_argument("--paths", metavar="STATUS", help="only print the paths with this status (FAILED, GONE, ...)")
    args = ap.parse_args()

    cfg = load_cfg()
    if not args.paths:
        tee_to_log(cfg)
    manifest = args.manifest or os.path.join(cfg["DOWNLOAD_TO"], "MANIFEST")
    if not os.path.exists(manifest):
        sys.exit("No MANIFEST at %s.  Nothing has been downloaded with tis-fetch.py there yet." % manifest)
    entries = read_manifest(manifest)
    root = cfg["FSM_URLBASE"]
    gone = [p for p, e in entries.items() if e[0] == "OK" and not on_disk(root, p)]
    # Not problems: files a script made locally instead (dl-html-ewd.sh's .svgz and compact diagrams), and
    # folder URLs an older dl-html-ewd.sh built from DOS line endings
    filled = [p for p, e in entries.items() if e[0] in ("MISSING", "FORBIDDEN") and not p.endswith("/") and on_disk(root, p)]
    bogus = [p for p, e in entries.items() if e[0] in ("MISSING", "FORBIDDEN") and p.endswith("/") and "/ewd/contents/" in p]
    skip = set(filled) | set(bogus)

    if args.paths:
        want = args.paths.upper()
        for p in (gone if want == "GONE" else [p for p, e in entries.items() if e[0] == want]):
            print(p)
        return 0

    if args.retry:
        want = {s.strip().upper() for s in args.retry.split(",")}
        unknown = want - {"FORBIDDEN", "MISSING", "GONE", "FAILED"}
        if unknown:
            ap.error("--retry takes FORBIDDEN, MISSING and GONE, not %s" % ", ".join(sorted(unknown)))
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        marked = collections.Counter()
        with open(manifest, "a", encoding="utf-8") as fh:
            for p, e in entries.items():
                was = "GONE" if p in gone else e[0]
                if was in want and was != "FAILED" and p not in skip:
                    fh.write("FAILED\t%s\t0\t%s\tmarked for retry by tis-report.py (was %s)\n" % (p, stamp, was))
                    marked[manual_of(p)] += 1
        if not marked:
            print("Nothing to mark.")
            return 0
        total = sum(marked.values())
        print("Marked %d file%s for download.  Run these from %s:" % (total, "" if total == 1 else "s", cfg["DOWNLOAD_TO"]))
        for (label, cmd), n in sorted(marked.items()):
            print("    %s/%s      # %s: %d file%s" % (cfg["SCRIPT_BASE"], cmd, label, n, "" if n == 1 else "s"))
        return 0

    # ---- report ----
    per_manual = collections.OrderedDict()
    for p, e in entries.items():
        key = manual_of(p)
        per_manual.setdefault(key, collections.Counter())[e[0]] += 1
    gone_by = collections.Counter(manual_of(p) for p in gone)

    print("MANIFEST: %s (%d files)\n" % (manifest, len(entries)))
    w = max(len(k[0]) for k in per_manual)
    print("%-*s %8s %8s %10s %7s %6s" % (w, "Manual", "OK", "MISSING", "FORBIDDEN", "FAILED", "GONE"))
    for key, c in sorted(per_manual.items()):
        print("%-*s %8d %8d %10d %7d %6d" % (w, key[0], c["OK"], c["MISSING"], c["FORBIDDEN"], c["FAILED"], gone_by[key]))

    def listing(title, paths, hint):
        if not paths:
            return
        print("\n%s (%d)  %s" % (title, len(paths), hint))
        for p in paths:
            note = entries[p][3]
            print("    %s%s" % (p, "  (%s, %s)" % (note, entries[p][2]) if note else ""))

    failed = [p for p, e in entries.items() if e[0] == "FAILED"]
    forbidden = [p for p, e in entries.items() if e[0] == "FORBIDDEN" and p not in skip]
    listing("FAILED", failed, "- rerunning the download retries these")
    listing("FORBIDDEN", forbidden, "- TIS refused these while the session worked; --retry FORBIDDEN to try again")
    listing("GONE", gone, "- OK in the MANIFEST but not on disk; --retry GONE to download them again")
    if filled or bogus:
        print("\nNot problems:")
        if filled:
            print("    %5d  MISSING/FORBIDDEN on TIS, but made locally by the download script (ie: .svgz from .svg)" % len(filled))
        if bogus:
            print("    %5d  folder URLs from an older dl-html-ewd.sh bug (ignore)" % len(bogus))

    missing = [p for p, e in entries.items() if e[0] == "MISSING" and p not in skip]
    if missing:
        groups = collections.OrderedDict()
        for p in missing:
            why = normal_missing(p)
            folder = p.rsplit("/", 1)[0] + "/"
            folder = re.sub(r"/contents/tree/\d+/$", "/contents/tree/*/", folder)
            groups.setdefault((why or "", folder), []).append(p)
        unusual = sum(len(v) for (why, _), v in groups.items() if not why)
        print("\nMISSING (%d, %d of them not known to be normal)  - TIS answered 404" % (len(missing), unusual))
        for (why, folder), paths in sorted(groups.items(), key=lambda g: (g[0][0] != "", g[0][1])):
            print("    %5d  %s%s" % (len(paths), folder, "  [normal: %s]" % why if why else ""))
            if args.verbose or (not why and len(paths) <= 5):
                for p in paths:
                    print("             %s" % p.rsplit("/", 1)[1])

    todo = collections.Counter(manual_of(p) for p in failed)
    todo.update(manual_of(p) for p in gone)
    todo.update(manual_of(p) for p in forbidden)
    print("\nTo download what's left:")
    if not todo:
        print("    Nothing.  Everything is OK or known to be missing on TIS.")
    else:
        if gone or forbidden:
            what = " and ".join(s for s, l in (("GONE", gone), ("FORBIDDEN", forbidden)) if l)
            print("    %s/tis-report.py --retry %s      # first, so the rerun includes them"
                  % (cfg["SCRIPT_BASE"], what.replace(" and ", ",")))
        print("    cd %s" % cfg["DOWNLOAD_TO"])
        for (label, cmd), n in sorted(todo.items()):
            print("    %s/%s      # %s: %d file%s" % (cfg["SCRIPT_BASE"], cmd, label, n, "" if n == 1 else "s"))
        print("    (If the session has expired, run %s/tis-login.sh first.)" % cfg["SCRIPT_BASE"])

    log = cfg.get("TIS_LOG") or os.path.join(cfg["DOWNLOAD_TO"], "tis-clone.log")
    runs = bad_runs(log)
    if runs:
        print("\nRecent runs that didn't finish cleanly (%s):" % log)
        meaning = {"1": "some files FAILED", "75": "session expired", "130": "interrupted"}
        for when, rc, cmd in runs:
            print("    %s  exit %-3s %-18s %s" % (when, rc, "(%s)" % meaning[rc] if rc in meaning else "", cmd))

    return 1 if failed or forbidden or gone else 0


if __name__ == "__main__":
    sys.exit(main())
