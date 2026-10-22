#!/usr/bin/env python3
#
# build-search.py - Make the search index for each manual's search box (website-framework/framework/tis-search.js)
#
# The website has to work on any plain web server (tis-serve.py, Apache, nginx, Abyss), so the searching
# happens in the browser, against index files made here.  They're small .js files the page loads with a
# <script> tag, only once someone searches, so they don't slow the site down and need no server set-up:
#
#   search/meta.js      the index pieces that exist, page count, ...
#   search/w/P0.js      every word starting with P0: the pages it's on (in the text and in the title)
#   search/p/3.js       pages 1500-1999: link, title, section (toc.xml path), to list the results
#
# Pages are numbered in toc.xml order; a page list is the gaps between page numbers, in hex.  Repair,
# body/collision and new car features manuals are indexed by their text; Reference Information, bulletins
# and the Flat Rate Manual (mostly PDFs or tables) by title only.  A manual whose index is newer than its
# toc.xml and pages is skipped.  toc2html.py adds the search box to a manual that has an index.
#
# Usage:
#   build-search.py [--force] [FSM_URLBASE | toc.xml ...]
#

import html
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

VERSION = 1                             # bump when the index format changes, to rebuild every index
CHUNK = 500                             # pages per search/p/N.js
WORD_RE = re.compile(r"[A-Za-z0-9]+")
DROP_RE = re.compile(rb"<script.*?</script>|<style.*?</style>|<table[^>]*class=\"side\".*?</table>", re.S | re.I)
TAG_RE = re.compile(rb"<[^>]+>")
# "...: DTC CHART; 2013 MY Prius V [10/2012 - ]": every page in a manual says which vehicle it's for
VEHICLE_RE = re.compile(r";\s*\d{4}(\s*-\s*\d{4})?\s+MY\b.*$")


def fsm_urlbase():
    script = '. "$HOME/.tis/tis-clone.cfg" && printf "%s" "$FSM_URLBASE"'
    return subprocess.run(["sh", "-c", script], capture_output=True, check=True).stdout.decode()


def words(text):
    return {w for w in WORD_RE.findall(text.upper()) if len(w) > 1}


def page_text(path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return ""
    return html.unescape(TAG_RE.sub(b" ", DROP_RE.sub(b" ", data)).decode("utf-8", "replace"))


def read_toc(toc):
    """[(href, title, section)] in toc order, one per page"""
    pages = []
    seen = set()

    def walk(node, path):
        for it in node.findall("item"):
            name = " ".join((it.findtext("name") or "").split())
            href = it.get("href") or ""
            if href:
                key = href.split("?")[0]
                if key not in seen:
                    seen.add(key)
                    pages.append((key, VEHICLE_RE.sub("", name) or name, " › ".join(path)))
            # TIS repeats a heading under itself (General › TOC2 › TOC2); say it once
            walk(it, path if path and path[-1] == name else path + [name])
    walk(toc, [])
    return pages


def js(call, *args):
    return "TISSearch.%s(%s);\n" % (call, ",".join(json.dumps(a, ensure_ascii=False, separators=(",", ":")) for a in args))


def gaps(ids):
    out, prev = [], 0
    for i in ids:
        out.append(format(i - prev, "x"))
        prev = i
    return ",".join(out)


def build(root, toc_path, force=False):
    folder = os.path.dirname(toc_path)
    out = os.path.join(folder, "search")
    try:
        toc_xml = open(toc_path, "rb").read()
        toc = ET.fromstring(toc_xml)
    except (OSError, ET.ParseError) as e:
        print("    %s: can't read it (%s), skipping" % (toc_path, e))
        return
    titles_only = b"Made by tis-refsearch.py" in toc_xml or "/frmapp/" in toc_path
    pages = read_toc(toc)
    if not pages:
        return
    files = [os.path.join(root, href.split("#")[0].lstrip("/")) for href, _, _ in pages]

    # Up to date?  (newer than the toc.xml, every page and this script's index format)
    meta = os.path.join(out, "meta.js")
    if not force and os.path.exists(meta):
        built = os.path.getmtime(meta)
        newest = max([os.path.getmtime(toc_path)] + [os.path.getmtime(f) for f in files if os.path.exists(f)])
        with open(meta, encoding="utf-8") as fh:
            same = '"version":%d,' % VERSION in fh.read()
        if same and built > newest:
            return

    text, title = {}, {}
    for i, (href, name, _) in enumerate(pages):
        tw = words(name)
        for w in tw:
            title.setdefault(w, []).append(i)
        for w in tw if titles_only else tw | words(page_text(files[i])):
            text.setdefault(w, []).append(i)

    new = out + ".new"
    shutil.rmtree(new, ignore_errors=True)
    os.makedirs(os.path.join(new, "w"))
    os.makedirs(os.path.join(new, "p"))
    shards = {}
    for w in sorted(text):
        shards.setdefault(w[:2], {})[w] = [gaps(text[w]), gaps(title.get(w, []))]
    for key, entries in shards.items():
        with open(os.path.join(new, "w", key + ".js"), "w", encoding="utf-8") as fh:
            fh.write(js("words", key, entries))
    for c in range(0, len(pages), CHUNK):
        rows, sections = [], []
        for href, name, section in pages[c:c + CHUNK]:
            if section not in sections:
                sections.append(section)
            rows.append([href, name, sections.index(section)])
        with open(os.path.join(new, "p", "%d.js" % (c // CHUNK)), "w", encoding="utf-8") as fh:
            fh.write(js("pages", c // CHUNK, {"sections": sections, "pages": rows}))
    with open(os.path.join(new, "meta.js"), "w", encoding="utf-8") as fh:
        fh.write(js("meta", {"version": VERSION, "pages": len(pages), "chunk": CHUNK, "text": not titles_only,
                             "shards": "".join(sorted(shards))}))
    old = out + ".old"
    shutil.rmtree(old, ignore_errors=True)
    if os.path.exists(out):
        os.rename(out, old)
    os.rename(new, out)
    shutil.rmtree(old, ignore_errors=True)
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(out) for f in fs)
    print("    %s: %d pages, %d words%s, %d KB" % (os.path.relpath(folder, root), len(pages), len(text),
                                                  " (titles only)" if titles_only else "", size // 1024))


def main():
    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    if args and all(a.endswith(".xml") for a in args):
        tocs = [os.path.abspath(a) for a in args]
    else:
        root = args[0] if args else fsm_urlbase()
        tocs = []
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, "t3Portal/external")):
            dirnames.sort()
            if "toc.xml" in filenames and "toc.html" in filenames:
                tocs.append(os.path.join(dirpath, "toc.xml"))
    for toc in tocs:
        # The website root is the folder above t3Portal/; toc.xml links start with /t3Portal/
        build(toc[:toc.rindex("/t3Portal/")], toc, force)


if __name__ == "__main__":
    main()
