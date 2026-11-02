#!/usr/bin/env python3
#
# build-index.py - Print the front page (index.html) listing every downloaded manual
#
# Lists each manual's toc.html (made by toc2html.py) and each wiring diagram's termdata.xml, plus a link to
# PDFs/index.html if there are PDFs.  tis-clone runs it after downloading.  The manuals are grouped into a
# collapsible section per model (ie: "Toyota Land Cruiser", or a generation of it named in SERIES: "Toyota
# Land Cruiser 200-series"), and in it a collapsible subsection per model year ("Toyota 2016 Land Cruiser").
# A manual covering several years (ie: the 2016-2021 repair manual, a 2008-2016 body manual) is listed under
# each of them.  The make is written Toyota/Lexus/Scion whatever case TIS used.  The models are the ones the
# repair manuals name; Flat Rate Manuals, Reference Information and bulletins join one even when they name
# fewer models ("LX600" goes under "LX600 LX700H"), and a New Car Features book for several models (or "All")
# goes under the one it covers that year.  Anything else is under "Other", by title.
#
# It also writes fluids.html, listing each repair manual's fluid capacities: the SPECIFICATIONS ... SERVICE
# DATA pages that give a capacity (newer manuals have one MAINTENANCE page per model year range with all of
# them; older ones spread them over the engine cooling and lubrication, transmission, transfer, differential,
# ... pages).  The front page links to it after the manuals; with no capacity pages there's no fluids.html.
#
# Usage:
#   build-index.py [FSM_URLBASE] > $FSM_URLBASE/index.html
#

import collections
import html
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

TITLE_RE = re.compile(r"<title>\s*(.*?)\s*</title>", re.S)
MAKES = {"TOYOTA": "Toyota", "LEXUS": "Lexus", "SCION": "Scion"}
# Sections for a model's generations: make, model (spaces and case ignored), years, section, model in the
# year subsections ("Lexus 2024 LX600 & LX700H")
SERIES = [
    ("Toyota", "Land Cruiser", 1990, 1997, "Toyota Land Cruiser 80-series", None),
    ("Toyota", "Land Cruiser", 1998, 2007, "Toyota Land Cruiser 100-series", None),
    ("Toyota", "Land Cruiser", 2008, 2021, "Toyota Land Cruiser 200-series", None),
    ("Toyota", "Land Cruiser", 2024, 2099, "Toyota Land Cruiser 250-series", None),
    ("Lexus", "LX600 LX700H", 1900, 2099, "Lexus LX600 & LX700H (300-series)", "LX600 & LX700H"),
]
# Order of the manuals in a year: (title has, place), checked in this order ("Collision Repair Manual"
# before "Repair Manual")
KINDS = [("Collision Repair", 2), ("Body Repair", 2), ("Transmission", 4), ("Repair Manual", 0),
         ("Electrical Wiring", 1), ("New Car Features", 3), ("Flat Rate", 5), ("Reference Information", 6),
         ("Service Bulletins", 7)]
# "TOYOTA 2016-2021 Land Cruiser Repair Manual (RM27J0U)": make, years, models, what it is
PARTS_RE = re.compile(r"^(?:(\w+)\s+)?((?:19|20)\d\d)(?:\s*-\s*((?:19|20)\d\d))?\s+(.*?)\s*"
                      r"((?:Repair Manual|Collision Repair|Body Repair|New Car Features|Electrical Wiring|Flat Rate"
                      r"|Reference Information|Service Bulletins|Automatic Transmission|\S+ Automatic Transmission)\b.*)?$",
                      re.I)
CAPACITY_RE = re.compile(rb"capacit", re.I)


def fsm_urlbase():
    script = '. "$HOME/.tis/tis-clone.cfg" && printf "%s" "$FSM_URLBASE"'
    return subprocess.run(["sh", "-c", script], capture_output=True, check=True).stdout.decode()


def manuals(root):
    """(title, link) for each manual, title already HTML"""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        if "toc.html" in filenames:
            with open(os.path.join(dirpath, "toc.html"), encoding="utf-8", errors="replace") as fh:
                m = TITLE_RE.search(fh.read(4096))
            if m:
                found.append((m.group(1), os.path.relpath(os.path.join(dirpath, "index.html"), root)))

    # Wiring diagrams: $FSM_URLBASE/t3Portal/external/en/ewdappu/EM30B0U/xhtml/termdata.xml
    ewd = os.path.join(root, "t3Portal/external/en/ewdappu")
    for name in sorted(os.listdir(ewd)) if os.path.isdir(ewd) else []:
        try:
            title = ET.parse(os.path.join(ewd, name, "xhtml/termdata.xml")).getroot().findtext(".//pubtitle")
        except (OSError, ET.ParseError):
            continue                        # not a manual, or a saved error page
        if title:
            title = title.strip()
            found.append((html.escape(title, quote=False),
                          "t3Portal/ewdappu/index.jsp?ewdNo=%s&locale=en&t3id=%s_INTRO01" % (name, name)))
    return [(camel(t), link) for t, link in sorted(found)]


def camel(title):
    """The make as Toyota, Lexus or Scion, and "manual" capitalised as in the other titles"""
    first, _, rest = title.partition(" ")
    title = "%s %s" % (MAKES.get(first.upper(), first), rest) if rest else title
    return re.sub(r"\bmanual\b", "Manual", title)


def parse(title):
    """(make, first year, last year, model words) of a title, or None"""
    m = PARTS_RE.match(html.unescape(title))
    if not m or not m.group(4):
        return None
    make = MAKES.get((m.group(1) or "").upper(), "")
    words = re.sub(r"\s*\([A-Za-z0-9]+\)$", "", m.group(4)).split()
    return make, int(m.group(2)), int(m.group(3) or m.group(2)), words


def squash(words):
    return "".join(words).upper()


def by_model(found):
    """[(section, [(year subsection, [(title, link)])])], a section per model (or SERIES generation) and in it
    a subsection per year; "Other" last, its one subsection unnamed"""
    parsed = [(t, link, parse(t)) for t, link in found]
    # The models: what the repair manuals name ({squashed: (make, words, [(first, last)])})
    models = {}
    for t, link, p in parsed:
        if p and re.search(r"\bRepair Manual\b", t) and "Collision" not in t and p[3] and p[3][0].upper() != "ALL":
            m = models.setdefault(squash(p[3]), (p[0], p[3], []))
            m[2].append((p[1], p[2]))

    def model_of(p):
        make, first, last, words = p
        same_make = [k for k, m in models.items() if not make or not m[0] or m[0] == make]
        if squash(words) in models:
            return squash(words)
        up = [w.upper() for w in words]
        # Fewer models (LX600 of LX600 LX700H), or several including it (1999 ES300 ... LX470 ...)
        fits = [k for k in same_make if set(up) <= {w.upper() for w in models[k][1]}
                or {w.upper() for w in models[k][1]} <= set(up)
                or squash(words).find(k) >= 0 and len(words) > len(models[k][1])]
        if not fits and up == ["ALL"]:
            fits = same_make
        if len(fits) > 1:
            covering = [k for k in fits if any(a <= first and last <= b for a, b in models[k][2])]
            fits = covering or fits
        return fits[0] if fits else None

    def kind(title):
        return next((place for has, place in KINDS if has.upper() in title.upper()), len(KINDS))

    sections = {}       # (make, model, first year of section): {"name":, "years": {year: [(kind, title, link)]}}
    for t, link, p in parsed:
        key = model_of(p) if p else None
        if not key:
            sections.setdefault(("~", "Other", 0), {"name": "Other", "years": {}})["years"] \
                .setdefault(None, []).append((t.upper(), t, link))
            continue
        make, words = models[key][0] or p[0], models[key][1]
        for year in range(p[1], p[2] + 1):
            series = next((x for x in SERIES if x[0] == make and squash(x[1].split()) == key
                           and x[2] <= year <= x[3]), None)
            if series:
                skey, name, label = (make, key, series[2]), series[4], series[5] or " ".join(words)
            else:
                skey, name, label = (make, key, 0), " ".join([make] + words).strip(), " ".join(words)
            sec = sections.setdefault(skey, {"name": name, "years": {}})
            sec["years"].setdefault(year, []).append((kind(t), t, link))
            sec.setdefault("label", label)
    out = []
    for skey in sorted(sections, key=lambda k: (k[0].upper(), k[1], k[2])):
        sec = sections[skey]
        years = []
        for year in sorted(sec["years"], key=lambda y: y or 0):
            label = "%s %d %s" % (skey[0], year, sec["label"]) if year else ""
            years.append((label, [(t, link) for k, t, link in sorted(sec["years"][year])]))
        out.append((sec["name"], years))
    return out


def fluid_pages(root):
    """[(manual title, [(label, link)])] of the repair manuals' service data pages that give capacities"""
    found = []
    rm = os.path.join(root, "t3Portal/external/en/rm")
    for name in sorted(os.listdir(rm)) if os.path.isdir(rm) else []:
        try:
            toc = ET.parse(os.path.join(rm, name, "toc.xml")).getroot()
        except (OSError, ET.ParseError):
            continue
        pages = []

        def walk(node, path):
            for it in node.findall("item"):
                label = " ".join((it.findtext("name") or "").split())
                href = (it.get("href") or "").split("?")[0]
                if href and "SERVICE DATA" in label.upper() and any(p.upper() == "SPECIFICATIONS" for p in path):
                    try:
                        with open(os.path.join(root, href.lstrip("/")), "rb") as fh:
                            gives = CAPACITY_RE.search(fh.read())
                    except OSError:
                        gives = None
                    if gives:
                        # "SERVICE DATA; 2022 - 2024 MY LX600 [12/2021 - 11/2024]" under MAINTENANCE
                        years = label.split(";", 1)[1].split("[")[0].strip() if ";" in label else ""
                        pages.append(("%s%s" % (path[-1] if path else "", " (%s)" % years if years else ""), href))
                walk(it, path + [label])
        walk(toc, [])
        # A MAINTENANCE page has all of them; then the others only mention a capacity in passing
        maintenance = [p for p in pages if p[0].upper().startswith("MAINTENANCE")]
        pages = maintenance or pages
        if pages:
            found.append((camel(" ".join((toc.findtext("name") or name).split())), sorted(set(pages))))
    return found


def fluids_page(fluids):
    out = ['<!DOCTYPE html><html><head><title>Fluid Capacities</title>\n'
           '<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width">\n'
           '<link rel="stylesheet" href="/framework/bootstrap.min.css"></head>\n'
           '<body>\n'
           '<a class="nav-link" href="/index.html">&lt; Home</a>\n'
           '<div class="nav-link"><b>Fluid Capacities</b><br>\n']
    for title, pages in fluids:
        out.append("<br>%s:<br>\n" % html.escape(title, quote=False))
        for label, link in pages:
            out.append("&nbsp;&nbsp;<a href='%s'>%s</a><br>\n" % (html.escape(link), html.escape(label, quote=False)))
    out.append('</div>\n</body></html>')
    return "".join(out)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else fsm_urlbase()
    sections = by_model(manuals(root))
    fluids = fluid_pages(root)
    page = os.path.join(root, "fluids.html")
    if fluids:
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(fluids_page(fluids))
    elif os.path.exists(page):
        os.remove(page)
    out = ['<!DOCTYPE html><html><head><title>Service Manuals</title>\n'
           '<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width">\n'
           '<link rel="stylesheet" href="/framework/bootstrap.min.css"></head>\n'
           '<body style="padding:0px; margin:0px;">\n'
           '<img src="t3Portal/resources/images/globals/header/headerbar.bg.blu.gif" '
           'style="width:100%; height:40px; margin:0px; border:0px; padding:0px">\n'
           '<ul class="nav flex-column flex-nowrap">\n']
    # One model: open; several: closed, click to open.  Years: closed (a model with one year: open).
    shown = " show" if len(sections) == 1 else ""
    for n, (name, years) in enumerate(sections, 1):
        out.append('  <li class="nav-item drop">\n'
                   '  <a class="nav-link%s" href="#model%d" data-toggle="collapse">+ %s</a>\n'
                   '  <div class="collapse%s" id="model%d">\n'
                   '  <ul class="flex-column nav" style="padding:0px 0px 0px 40px;">\n'
                   % ("" if shown else " collapsed", n, html.escape(name, quote=False), shown, n))
        year_shown = " show" if len(years) == 1 else ""
        for y, (label, docs) in enumerate(years, 1):
            indent = "    "
            if label:
                out.append('    <li class="nav-item"><a class="nav-link py-1%s" href="#model%dyear%d" data-toggle="collapse">- %s</a>\n'
                           '    <div class="collapse%s" id="model%dyear%d">\n'
                           '    <ul class="flex-column nav" style="padding:0px 0px 0px 30px;">\n'
                           % ("" if year_shown else " collapsed", n, y, html.escape(label, quote=False), year_shown, n, y))
                indent = "      "
            for title, link in docs:
                out.append("%s<li class='nav-item'><a class='nav-link py-0' href='/%s'>%s</a></li>\n"
                           % (indent, html.escape(link), title))
            if label:
                out.append('    </ul></div></li>\n')
        out.append('  </ul></div></li>\n')
    out.append('</ul>\n')
    if fluids:
        out.append('<div class="nav-link"><a href="fluids.html">Fluid Capacities</a></div>\n')
    if os.path.isdir(os.path.join(root, "PDFs")):
        out.append('<div class="nav-link"><a href="PDFs/index.html">PDF File Index</a></div>\n')
    out.append('<script src="/framework/jquery-3.4.1.min.js"></script>\n'
               '<script src="/framework/popper.min.js"></script>\n'
               '<script src="/framework/bootstrap.min.js"></script>\n'
               '</body></html>')
    sys.stdout.buffer.write("".join(out).encode("utf-8"))

if __name__ == "__main__":
    main()
