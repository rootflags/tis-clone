#!/usr/bin/env python3
#
# tis-frm.py - Save a vehicle's Flat Rate Manual (labor times) from TIS's Flat Rate Manual application
#
# Newer vehicles' Flat Rate Manual isn't a document but an application (TIS > Vehicle Inquiry > Flat Rate
# Manual): a tree of Accessories, Maintenance and Repair sections, each a table of operations with the labor
# hours for every VDS (characters 4-8 of the VIN: the model's engine/grade variants).  This saves all of it
# for each model year as web pages, one per section with a column per VDS, plus TIS's general information
# PDF, in $FSM_URLBASE/t3Portal/external/en/frmapp/DIVISION_MODEL_YEAR/ with a toc.xml, so it shows up on the
# front page like a manual and tis-pdfbook.py can make it a PDF.
#
# How the application works (all ordinary requests in one session):
#   GET  /t3Portal/appmanager/t3/frm?titleDetails=frm&division=&model=&year=   the page, with the whole
#        tree (treeArray: [branch, '', branch, [section, 'sectionId=N', ...[page, 'pageId=N', ...]]]) and
#        the VDS list (<select id="selectVDS">)
#   POST its flateRateManualLookupForm with actionName=dmyLookup and up to 3 VDS: show those VDS columns
#   POST its flateRateManualTreeForm with sectionId=N: that section's table (Component, Operation, Type,
#        Operation Number, Hours (VDS) x3; the hours are the value of read-only inputs)
# Every section is fetched for every group of 3 VDS and the rows are merged by operation number.  Results are
# kept in $DOWNLOAD_TO/frmwork/, so a rerun only fetches what's missing.
#
# Usage:
#   tis-frm.py DIVISION MODEL YEARS          ie: tis-frm.py LEXUS LX600 2024, TOYOTA "Land Cruiser" 2016-2018
#                                            (YEARS: 2024, 2022-2024, 2022,2024-2025)
#   tis-frm.py --pdf DIVISION MODEL YEARS    make PDFs of what's been saved (no TIS requests), in
#                                            $FSM_URLBASE/PDFs/<vehicle>/FlatRateManual-DIVISION_MODEL_YEAR.pdf
#
# Exit status: 0 done, 1 something failed, 75 the session expired and could not log in again.
#

import argparse
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.parse

from tislog import tee_to_log

here = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location("tis_refsearch", os.path.join(here, "tis-refsearch.py"))
tis_refsearch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tis_refsearch)
SearchFailed = tis_refsearch.SearchFailed

APP = "/t3Portal/appmanager/t3/frm?titleDetails=frm&division=%s&model=%s&year=%s&searchKeyword=&language=en"
HELP_PDF = "/t3Portal/staticcontent/en/frm/help/%s.pdf"
TREE_RE = re.compile(r"treeArray\.push\((\[.*?\])\);", re.S)
VDS_RE = re.compile(r'<select[^>]*id="selectVDS".*?</select>', re.S)
ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td\b[^>]*>(.*?)</td>", re.S)
HOURS_RE = re.compile(r'class="transparentBg" value="([^"]*)"')
TOKEN_RE = re.compile(r"\s*(?:([\[\],])|'((?:\\.|[^'\\])*)')")


def js_array(text):
    """Parse a JavaScript array literal of single-quoted strings, ie: ['a', 'b', ['c']]"""
    stack, cur, pos = [], None, 0
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            raise ValueError("can't read the tree at: %r" % text[pos:pos + 40])
        pos = m.end()
        if m.group(1) == "[":
            new = []
            if cur is not None:
                cur.append(new)
                stack.append(cur)
            cur = new
        elif m.group(1) == "]":
            if not stack:
                return cur
            cur = stack.pop()
        elif m.group(2) is not None:
            cur.append(" ".join(html.unescape(re.sub(r"\\(.)", r"\1", m.group(2))).split()))
    return cur


def read_app(page):
    """[(branch, [(sectionId, section, [(pageId, page)])])] and the VDS list from the application page"""
    tree = []
    for m in TREE_RE.finditer(page):
        for branch in js_array(m.group(1)):
            sections = []
            for sec in branch[3:]:
                pages = [(p[1].split("=")[1], p[0]) for p in sec[3:] if isinstance(p, list) and p[1].startswith("pageId=")]
                if sec[1].startswith("sectionId="):
                    sections.append((sec[1].split("=")[1], sec[0], pages))
            tree.append((branch[0], sections))
    m = VDS_RE.search(page)
    vds = re.findall(r'<option[^>]*value="([^"]+)"', m.group(0)) if m else []
    return tree, vds


def form(page, name):
    """(url, [(field, value)]) of a form on the page, without its buttons"""
    a = page.find('name="%s"' % name)
    if a < 0:
        raise SearchFailed("the Flat Rate Manual page has no %s" % name)
    f = page[a:page.find("</form>", a)]
    u = urllib.parse.urlsplit(html.unescape(re.search(r'action="([^"]+)"', f).group(1)))
    data = []
    for t in re.findall(r"<input\b[^>]*>", f):
        n, v, ty = (re.search(r'%s="([^"]*)"' % a, t) for a in ("name", "value", "type"))
        if n and not (ty and ty.group(1) in ("submit", "button")):
            data.append((html.unescape(n.group(1)), html.unescape(v.group(1)) if v else ""))
    return u.path + "?" + u.query, data


def setf(data, name, *values):
    data[:] = [(n, v) for n, v in data if n != name] + [(name, v) for v in values]


def read_rows(page, vds):
    """[{component, operation, type, op, hours: {vds: hours}}] from a section's table"""
    seg = page[page.find("t_FlatRateManualDetails"):]
    rows, component = [], ""
    for r in ROW_RE.findall(seg):
        tds = TD_RE.findall(r)
        cells = [html.unescape(re.sub(r"<[^>]+>|\s+", " ", t)).strip() for t in tds]
        if len(tds) == 4 + len(vds):
            component = cells[0]
            tds, cells = tds[1:], cells[1:]
        if len(tds) != 3 + len(vds) or cells[0] == "Operation":
            continue
        hours = {}
        for v, td in zip(vds, tds[3:]):
            m = HOURS_RE.search(td)
            if m:
                hours[v] = m.group(1)
        rows.append({"component": component, "operation": cells[0], "type": cells[1], "op": cells[2], "hours": hours})
    return rows


class FRM:
    def __init__(self, rs, division, model, year, cache):
        self.rs, self.division, self.model, self.year = rs, division, model, year
        self.cache_file = cache
        try:
            with open(cache) as fh:
                self.cache = json.load(fh)
        except (OSError, ValueError):
            self.cache = {}
        self.page = None                # the application page, for its forms
        self.showing = None             # the VDS group the session is showing

    def save(self):
        tmp = self.cache_file + ".part"
        with open(tmp, "w") as fh:
            json.dump(self.cache, fh)
        os.replace(tmp, self.cache_file)

    def open_app(self):
        q = urllib.parse.quote
        self.page = self.rs.request("GET", APP % (q(self.division), q(self.model), self.year))
        if "Technical Error" in self.page:
            raise SearchFailed("TIS couldn't open the Flat Rate Manual for %s %s %s" % (self.division, self.model, self.year))
        tree, vds = read_app(self.page)
        m = re.search(r'id="dmyVdsValuesId" value="([^"]*)"', self.page)
        self.showing = m.group(1).split(",") if m else None
        if "tree" not in self.cache:
            self.cache.update(tree=tree, vds=vds)
            self.save()

    def show(self, group):
        """Make the session show these VDS columns"""
        if self.page is None:
            self.open_app()
        if self.showing == group:
            return
        url, data = form(self.page, "flateRateManualLookupForm")
        setf(data, "FlatRateManualLookup{actionForm.actionName}", "dmyLookup")
        setf(data, "FlatRateManualLookup{actionForm.dmyVds}", ",".join(group))
        for name, value in (("division", self.division), ("model", self.model), ("year", self.year)):
            setf(data, "FlatRateManualLookupwlw-select_key:{actionForm.%s}" % name, value)
        setf(data, "FlatRateManualLookupwlw-select_key:{actionForm.vds}", *group)
        data.append(("FlatRateManualLookupactionOverride:resetActionName", "Lookup"))
        self.page = self.rs.request("POST", url, data)
        m = re.search(r'id="dmyVdsValuesId" value="([^"]*)"', self.page)
        if not m or m.group(1).split(",") != group:
            raise SearchFailed("TIS didn't switch to VDS %s" % ",".join(group))
        self.showing = group

    def section(self, group, section_id):
        """Fetch one section for one VDS group (once: the result is cached)"""
        key = "%s|%s" % (",".join(group), section_id)
        if key in self.cache.get("sections", {}):
            return
        self.show(group)
        url, data = form(self.page, "flateRateManualTreeForm")
        setf(data, "FlatRateManualTree{actionForm.sectionId}", section_id)
        setf(data, "FlatRateManualTree{actionForm.pageId}", "")
        page = self.rs.request("POST", url, data)
        if "Technical Error" in page:
            raise SearchFailed("TIS error on section %s" % section_id)
        self.cache.setdefault("sections", {})[key] = read_rows(page, group)
        self.save()

    def run(self):
        """Fetch everything not cached yet"""
        def start():
            self.page = None
            self.open_app()
        if "tree" not in self.cache:
            self.rs.retrying(start)
        vds, tree = self.cache["vds"], self.cache["tree"]
        if not vds or not tree:
            return False
        groups = [vds[i:i + 3] for i in range(0, len(vds), 3)]
        todo = [(g, sid) for g in groups for branch, sections in tree for sid, name, pages in sections]
        done = 0
        for g, sid in todo:
            def one():
                try:
                    self.section(g, sid)
                except tis_refsearch.tis_fetch.SessionDead:
                    self.page = None        # a new session has to open the application again
                    raise
            self.rs.retrying(one)
            done += 1
            if done % 10 == 0:
                print("    %d of %d sections" % (done, len(todo)), flush=True)
        return True


def merged(cache, section_id):
    """A section's rows with the hours of every VDS, in TIS's order"""
    rows, by_op = [], {}
    for key, part in cache.get("sections", {}).items():
        if key.split("|")[1] != section_id:
            continue
        for r in part:
            k = (r["component"], r["op"], r["operation"])
            if k not in by_op:
                by_op[k] = dict(r, hours=dict(r["hours"]))
                rows.append(by_op[k])
            else:
                by_op[k]["hours"].update(r["hours"])
    return rows


PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>%(title)s</title>
<style>
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; margin: 8px; }
table { border-collapse: collapse; width: 100%%; }
th, td { border: 1px solid #999; padding: 2px 4px; vertical-align: top; }
th { background: #ddd; }
td.h { text-align: right; white-space: nowrap; }
td.c { white-space: nowrap; }
tr.component td { background: #eef; font-weight: bold; }
</style></head>
<body>
<h2>%(title)s</h2>
<p>%(vehicle)s.  Hours per VDS (characters 4-8 of the VIN).  Types: R&amp;R remove and replace, RPL replace,
CHG change, ADJ adjust, INS inspect, GND grind, OTH other.</p>
<table>
<tr><th>Operation</th><th>Type</th><th>Operation Number</th>%(vds_heads)s</tr>
%(rows)s
</table>
</body></html>
"""


def write_manual(cache, out, division, model, year):
    """The web pages and toc.xml for one model year"""
    e = lambda s: html.escape(s, quote=False)
    vds = cache["vds"]
    vehicle = "%s %s %s" % (year, division.title(), model)
    os.makedirs(os.path.join(out, "xhtml"), exist_ok=True)
    folder = "/" + os.path.relpath(out, ROOT).replace(os.sep, "/")
    toc = ['<?xml version="1.0" encoding="UTF-8"?>\n<!-- Made by tis-frm.py from the TIS Flat Rate Manual application -->\n'
           "<xmltoc>\n  <name>%s %s %s Flat Rate Manual</name>\n" % (e(division), year, e(model))]
    # General information (TIS's PDF for the division): a page that opens it, and that tis-pdfbook.py includes
    pdf = HELP_PDF % division
    with open(os.path.join(out, "xhtml", "general.html"), "w") as fh:
        fh.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>General Information</title>\n'
                 '<link rel="pdf" href="%s"></head>\n<body><script>location="%s";</script>'
                 '<a href="%s">General Information (PDF)</a></body></html>\n' % (pdf, pdf, pdf))
    toc.append('  <item href="">\n    <name>General</name>\n    <item href="">\n      <name>General</name>\n'
               '      <item href="%s/xhtml/general.html">\n        <name>General Information</name>\n      </item>\n'
               "    </item>\n  </item>\n" % folder)
    count = 0
    for branch, sections in cache["tree"]:
        toc.append('  <item href="">\n    <name>%s</name>\n' % e(branch))
        for sid, name, pages in sections:
            rows = merged(cache, sid)
            ids = {}
            for pid, pname in pages:
                ids.setdefault(pname, pid)
            body, last, anchors = [], None, []
            for r in rows:
                if r["component"] != last:
                    last = r["component"]
                    label = "Other" if last in ("", "NULL") else last
                    anchor = "p" + ids.get(last, str(len(anchors)))
                    anchors.append((anchor, label))
                    body.append('<tr class="component"><td colspan="%d"><a name="%s"></a>%s</td></tr>' % (3 + len(vds), anchor, e(label)))
                body.append("<tr><td>%s</td><td class=\"c\">%s</td><td class=\"c\">%s</td>%s</tr>" % (
                    e(r["operation"]), e(r["type"]), e(r["op"]),
                    "".join('<td class="h">%s</td>' % e(r["hours"].get(v, "")) for v in vds)))
            count += len(rows)
            with open(os.path.join(out, "xhtml", "%s.html" % sid), "w") as fh:
                fh.write(PAGE % {"title": e("%s: %s" % (branch, name)), "vehicle": e(vehicle),
                                 "vds_heads": "".join("<th>%s</th>" % e(v) for v in vds), "rows": "\n".join(body)})
            toc.append('    <item href="">\n      <name>%s</name>\n' % e(name))
            for anchor, label in anchors or [("", name)]:
                toc.append('      <item href="%s/xhtml/%s.html%s">\n        <name>%s</name>\n      </item>\n'
                           % (folder, sid, "#" + anchor if anchor else "", e(label)))
            toc.append("    </item>\n")
        toc.append("  </item>\n")
    toc.append("</xmltoc>\n")
    with open(os.path.join(out, "toc.xml.part"), "w") as fh:
        fh.write("".join(toc))
    os.replace(os.path.join(out, "toc.xml.part"), os.path.join(out, "toc.xml"))
    return count


ROOT = None


def folder_name(division, model, year):
    return re.sub(r"[ /]", "_", "%s_%s_%s" % (division, model, year)).upper()


def make_pdfs(vehicle):
    """tis-pdfbook.py each saved year into PDFs/<vehicle, from toc2topic.py>/"""
    rc = 0
    for year in tis_refsearch.years_of(vehicle[2]):
        name = folder_name(vehicle[0], vehicle[1], year)
        toc = os.path.join(ROOT, "t3Portal/external/en/frmapp", name, "toc.xml")
        if not os.path.exists(toc):
            print("No Flat Rate Manual saved for %s %s %s (%s)" % (year, vehicle[0], vehicle[1], toc))
            continue
        topic = subprocess.run([os.path.join(here, "toc2topic.py"), toc], capture_output=True, text=True).stdout.strip()
        pdf = os.path.join(ROOT, "PDFs", topic or name, "FlatRateManual-%s.pdf" % name)
        os.makedirs(os.path.dirname(pdf), exist_ok=True)
        print("* Making %s" % pdf, flush=True)
        if subprocess.call([os.path.join(here, "tis-pdfbook.py"), toc, pdf]) != 0:
            rc = 1
    return rc


def main():
    global ROOT
    ap = argparse.ArgumentParser(description="Save a vehicle's Flat Rate Manual from TIS's Flat Rate Manual application")
    ap.add_argument("vehicle", nargs=3, metavar="DIVISION MODEL YEARS", help="ie: LEXUS LX600 2024 (YEARS: 2024, 2022-2024, 2022,2024)")
    ap.add_argument("--wait", type=float, default=1.0, help="seconds between requests (default 1)")
    ap.add_argument("--pdf", action="store_true", help="make PDFs of the saved Flat Rate Manuals (no TIS requests)")
    args = ap.parse_args()

    cfg = tis_refsearch.tis_fetch.load_cfg()
    tee_to_log(cfg)
    ROOT = os.path.realpath(cfg["FSM_URLBASE"])
    if args.pdf:
        return make_pdfs(args.vehicle)
    rs = tis_refsearch.RefSearch(cfg, args.wait)
    division, model = args.vehicle[0].upper(), args.vehicle[1]
    match = [m for m in rs.vehicles("model", division) if m.lower() == model.lower()]
    if not match:
        print("TIS has no %s model %s.  tis-refsearch.py --models %s lists them." % (division, model, division))
        return 1
    model = match[0]
    work = os.path.join(cfg["DOWNLOAD_TO"], "frmwork")
    os.makedirs(work, exist_ok=True)

    rc = 0
    for year in tis_refsearch.years_of(args.vehicle[2]):
        name = folder_name(division, model, year)
        print("Flat Rate Manual for the %s %s %s ..." % (year, division, model), flush=True)
        frm = FRM(rs, division, model, year, os.path.join(work, name + ".json"))
        try:
            if not frm.run():
                print("    TIS has no Flat Rate Manual for it.")
                continue
        except SearchFailed as e:
            print("    %s.  Rerun to try again." % e)
            rc = 1
            continue
        finally:
            rs.fetcher.save_cookies()
        out = os.path.join(ROOT, "t3Portal/external/en/frmapp", name)
        n = write_manual(frm.cache, out, division, model, year)
        subprocess.call([os.path.join(here, "tis-fetch.py"), "-q", HELP_PDF % division])
        with open(os.path.join(out, "toc.html"), "w") as fh:
            subprocess.call([os.path.join(here, "toc2html.py"), os.path.join(out, "toc.xml")], stdout=fh)
        subprocess.call(["cp", os.path.join(cfg["SCRIPT_BASE"], "..", "website-framework", "index.html"), out])
        print("    %d operations for %d VDS in %s" % (n, len(frm.cache["vds"]), out), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
