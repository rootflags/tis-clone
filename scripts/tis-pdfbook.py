#!/usr/bin/env python3
#
# tis-pdfbook.py - Make one PDF of a whole manual, with working links and bookmarks
#
# Renders every page listed in a manual's toc.xml with wkhtmltopdf and joins them, in toc.xml order, into a
# single PDF.  Links between pages (and to a spot inside a page) become internal PDF links, so they work in
# any PDF viewer: phone, tablet, browser or desktop.  The bookmarks follow toc.xml, like the website's
# navigation.
#
# How: the download is served on 127.0.0.1 (from port 8080, or the next free one) so wkhtmltopdf sees the
# pages exactly as a browser does; no /t3Portal link or web server setup is needed.  While serving, each
# <a name> anchor gets an id and a zero-height box (wkhtmltopdf can only place anchors that have both), and
# an invisible link to every anchor is added so wkhtmltopdf records where each one ends up.  Nothing on
# disk is changed.  Pages are rendered several at a time into $DOWNLOAD_TO/pdfwork, so an interrupted run
# picks up where it stopped.  Then pikepdf joins them and turns each link to http://127.0.0.1:PORT/... into
# a link to the right page and position.  Links to pages outside this manual go to $MYURL (if it's set to
# your website) or are removed.
#
# Older manuals whose pages are just a pointer to a PDF use that PDF as is.
#
# Usage:
#   tis-pdfbook.py TOC.XML OUT.PDF [-j JOBS] [--limit N]
#     ie: tis-pdfbook.py $FSM_URLBASE/t3Portal/external/en/rm/RM30B0U/toc.xml RepairManual-RM30B0U.pdf
#
# Requirements: wkhtmltopdf (the "with patched qt" build), python3-pikepdf
#

import argparse
import concurrent.futures
import hashlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET

import pikepdf

from tislog import tee_to_log

WORK_VERSION = "v1"         # bump when the rendering changes, so cached pages are made again
NAME_RE = re.compile(rb'<a\b([^>]*?)\bname="([^"]+)"([^>]*)>')
PDF_LINK_RE = re.compile(rb'<link[^>]*rel="pdf"[^>]*href="([^"]+\.pdf)"')

here = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location("tis_serve", os.path.join(here, "tis-serve.py"))
tis_serve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tis_serve)


class PrintHandler(tis_serve.Handler):
    """Serves manual pages ready for wkhtmltopdf (see the top of this file); everything else as is"""

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.translate_path(self.path)
        if not (path.endswith(".html") and "/xhtml/" in path and os.path.isfile(path)):
            return super().do_GET()
        with open(path, "rb") as fh:
            body = fh.read()
        names = [m.group(2) for m in NAME_RE.finditer(body)]
        body = NAME_RE.sub(lambda m: b'<a%sname="%s" id="%s" style="display:block;height:0"%s>'
                           % (m.group(1), m.group(2), m.group(2), m.group(3))
                           if b" id=" not in m.group(0) else m.group(0), body)
        if names:
            marks = b"".join(b'<a href="#%s">.</a>' % n for n in names)
            body = body.replace(b"</body>", b'<div style="font-size:1px;line-height:1px;color:transparent">'
                                + marks + b"</div></body>", 1)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def load_cfg():
    names = ["DOWNLOAD_TO", "FSM_URLBASE", "MYURL", "TIS_LOG"]
    script = '. "$HOME/.tis/tis-clone.cfg" && printf "%s\\0" ' + " ".join('"$%s"' % n for n in names)
    out = subprocess.run(["sh", "-c", script], capture_output=True, check=True).stdout
    return dict(zip(names, out.decode().split("\0")))


def read_toc(toc_file):
    """(title, tree, docs): tree is [(name, path or None, children)], docs the page paths in order"""
    root = ET.parse(toc_file).getroot()
    docs = []

    def walk(node):
        out = []
        for it in node.findall("item"):
            path = urllib.parse.urlsplit(it.get("href") or "").path or None
            if path and path not in docs:
                docs.append(path)
            out.append(((it.findtext("name") or "").strip(), path, walk(it)))
        return out

    tree = walk(root)
    return (root.findtext("name") or "").strip(), tree, docs


def page_pdf(doc, root, base, work):
    """Make the PDF for one page (or find the PDF it points to).  Returns (pdf file, problem or None)"""
    html = os.path.join(root, doc.lstrip("/"))
    if not os.path.isfile(html):
        return None, "not downloaded"
    with open(html, "rb") as fh:
        m = PDF_LINK_RE.search(fh.read())
    if m:
        # An older manual: the page only points at a PDF
        target = os.path.join(root, urllib.parse.urljoin(doc, m.group(1).decode()).lstrip("/"))
        with open(target, "rb") as fh:
            ok = fh.read(4) == b"%PDF"
        return (target, None) if ok else (None, "its PDF isn't downloaded")
    out = os.path.join(work, os.path.basename(doc)[:-5] + ".pdf")
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(html):
        return out, None
    tmp = out + ".part"
    cmd = ["wkhtmltopdf", "-q", "--load-error-handling", "ignore", "--load-media-error-handling", "ignore",
           base + doc, tmp]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=600)
    except subprocess.TimeoutExpired:
        return None, "wkhtmltopdf took too long"
    try:
        with open(tmp, "rb") as fh:
            ok = fh.read(4) == b"%PDF"
    except OSError:
        ok = False
    if not ok:
        return None, "wkhtmltopdf failed"
    os.replace(tmp, out)
    return out, None


def share_images(pdf):
    """The same images (icons, symbols) appear on many pages; keep one copy of each.  Returns bytes saved"""
    canon, done, saved = {}, {}, 0

    def one(img):
        nonlocal saved
        if img.objgen in done:
            return done[img.objgen]
        if "/SMask" in img:                 # the transparency mask is an image too; share it first
            img.SMask = one(img.SMask)
        raw = img.read_raw_bytes()
        key = (hashlib.sha1(raw).digest(),
               repr(sorted((k, repr(v) if k != "/SMask" else v.objgen) for k, v in img.items() if k != "/Length")))
        if key in canon:
            saved += len(raw)
        else:
            canon[key] = img
        done[img.objgen] = canon[key]
        return canon[key]

    def resources(res, seen):
        xobjects = res.get("/XObject") if res is not None else None
        if xobjects is None:
            return
        for name in list(xobjects.keys()):
            x = xobjects[name]
            if not isinstance(x, pikepdf.Stream) or x.objgen in seen:
                continue
            if x.get("/Subtype") == "/Image":
                xobjects[name] = one(x)
            elif x.get("/Subtype") == "/Form":
                seen.add(x.objgen)
                resources(x.get("/Resources"), seen)

    seen = set()
    for page in pdf.pages:
        resources(page.obj.get("/Resources"), seen)
    return saved


def main():
    ap = argparse.ArgumentParser(description="Make one PDF of a whole manual, with working links and bookmarks")
    ap.add_argument("toc", help="the manual's toc.xml")
    ap.add_argument("out", help="PDF to write")
    ap.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 2, help="pages to render at once")
    ap.add_argument("--limit", type=int, help="only the first N pages (for testing)")
    args = ap.parse_args()

    cfg = load_cfg()
    tee_to_log(cfg)
    root = cfg["FSM_URLBASE"]
    title, tree, docs = read_toc(args.toc)
    if args.limit:
        docs = docs[:args.limit]
    work = os.path.join(cfg["DOWNLOAD_TO"], "pdfwork", WORK_VERSION,
                        os.path.basename(os.path.dirname(os.path.abspath(args.toc))))
    os.makedirs(work, exist_ok=True)

    server = tis_serve.start_server(root, "127.0.0.1", 8080, PrintHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_address[1]
    print("%s: %d pages, rendering %d at a time (pages are served at %s)" % (title, len(docs), args.jobs, base), flush=True)

    # ---- render ----
    files, problems = {}, {}
    started = time.time()
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        jobs = {pool.submit(page_pdf, d, root, base, work): d for d in docs}
        for n, fut in enumerate(concurrent.futures.as_completed(jobs), 1):
            d = jobs[fut]
            f, why = fut.result()
            if f:
                files[d] = f
            else:
                problems[d] = why
                print("    %s: %s" % (d, why), flush=True)
            if n % 250 == 0 or n == len(docs):
                print("    %d of %d pages (%d min)" % (n, len(docs), (time.time() - started) // 60), flush=True)
    server.shutdown()

    # ---- join, recording where each page and anchor ended up ----
    out = pikepdf.new()
    start, anchors, sources = {}, {}, []
    for d in docs:
        if d not in files:
            continue
        try:
            with open(files[d], "rb") as fh:
                src = pikepdf.open(io.BytesIO(fh.read()))
        except (OSError, pikepdf.PdfError) as e:
            problems[d] = "unreadable PDF (%s)" % e
            print("    %s: %s" % (d, problems[d]), flush=True)
            continue
        sources.append(src)                     # pikepdf copies pages lazily; keep the source open
        start[d] = len(out.pages)
        index = {p.obj.objgen: i for i, p in enumerate(src.pages)}
        for name, dest in (src.Root.get("/Dests") or {}).items():
            u = urllib.parse.urlsplit(str(name).lstrip("/"))
            if not u.fragment or not isinstance(dest, pikepdf.Array) or len(dest) < 4:
                continue
            p = dest[0]
            i = int(p) if isinstance(p, int) else index.get(p.objgen)
            if i is not None:
                anchors[(u.path, u.fragment)] = (start[d] + i, dest[3])
        out.pages.extend(src.pages)

    # ---- links ----
    myurl = cfg["MYURL"].rstrip("/")
    if re.match(r"https?://(localhost|127\.)", myurl):
        myurl = ""
    counts = {"internal": 0, "website": 0, "removed": 0}
    for page in out.pages:
        annots = page.obj.get("/Annots")
        if annots is None:
            continue
        keep = []
        for a in annots:
            target = None
            if a.get("/Subtype") == "/Link":
                if "/Dest" in a and isinstance(a.Dest, (pikepdf.Name, pikepdf.String)):
                    target = str(a.Dest).lstrip("/")
                elif "/A" in a and "/URI" in a.A:
                    target = str(a.A.URI)
            if not target or not target.startswith(base):
                keep.append(a)
                continue
            if abs(float(a.Rect[2]) - float(a.Rect[0])) < 4:
                continue                    # one of our invisible links to the anchors; it's done its job
            u = urllib.parse.urlsplit(target)
            if (u.path, u.fragment) in anchors:
                i, y = anchors[(u.path, u.fragment)]
            elif u.path in start:
                i, y = start[u.path], out.pages[start[u.path]].mediabox[3]
            else:
                i = None
            if i is not None:
                a.Dest = pikepdf.Array([out.pages[i].obj, pikepdf.Name.XYZ, None, y, None])
                if "/A" in a:
                    del a["/A"]
                counts["internal"] += 1
                keep.append(a)
            elif myurl:
                a.A = pikepdf.Dictionary(S=pikepdf.Name.URI, URI=myurl + target[len(base):])
                if "/Dest" in a:
                    del a["/Dest"]
                counts["website"] += 1
                keep.append(a)
            else:
                counts["removed"] += 1      # points at our temporary server; would only ever be broken
        page.obj.Annots = pikepdf.Array(keep)

    # ---- bookmarks from toc.xml ----
    def first_page(node):
        name, path, children = node
        if path in start:
            return start[path]
        for c in children:
            p = first_page(c)
            if p is not None:
                return p
        return None

    def add(nodes, parent):
        for node in nodes:
            p = first_page(node)
            if p is None:
                continue
            item = pikepdf.OutlineItem(node[0] or "(untitled)", p)
            parent.append(item)
            add(node[2], item.children)

    with out.open_outline() as outline:
        add(tree, outline.root)

    saved = share_images(out)
    if saved:
        print("Shared %d MB of repeated images" % (saved // 1000000), flush=True)
    out.docinfo["/Title"] = title
    out.Root.PageMode = pikepdf.Name.UseOutlines

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    tmp = args.out + ".part"
    out.save(tmp, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    os.replace(tmp, args.out)
    print("Wrote %s: %d pages from %d of %d manual pages.  Links: %d inside the PDF, %d to %s, %d removed."
          % (args.out, len(out.pages), len(start), len(docs), counts["internal"], counts["website"],
             myurl or "your website (MYURL not set)", counts["removed"]))
    if problems:
        print("%d pages are missing from the PDF (see above)." % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
