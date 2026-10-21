#!/usr/bin/env python3
#
# build-index.py - Print the front page (index.html) listing every downloaded manual
#
# Lists each manual's toc.html (made by toc2html.py) and each wiring diagram's termdata.xml, sorted by
# title, plus a link to PDFs/index.html if there are PDFs.  tis-clone runs it after downloading.
#
# It also lists each repair manual's fluid capacities: the SPECIFICATIONS ... SERVICE DATA pages that give
# a capacity (newer manuals have one MAINTENANCE page per model year range with all of them; older ones
# spread them over the engine cooling and lubrication, transmission, transfer, differential, ... pages).
#
# Usage:
#   build-index.py [FSM_URLBASE] > $FSM_URLBASE/index.html
#

import html
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

TITLE_RE = re.compile(r"<title>\s*(.*?)\s*</title>", re.S)
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
            title = title.strip().replace("TOYOTA", "Toyota").replace("LEXUS", "Lexus").replace("SCION", "Scion")
            found.append((html.escape(title, quote=False),
                          "t3Portal/ewdappu/index.jsp?ewdNo=%s&locale=en&t3id=%s_INTRO01" % (name, name)))
    return sorted(found)


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
            found.append((" ".join((toc.findtext("name") or name).split()), sorted(set(pages))))
    return found


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else fsm_urlbase()
    out = ['<head><link rel="stylesheet" href="/framework/bootstrap.min.css"></head>\n'
           '<body style="padding:0px; margin:0px;">\n'
           '<img src="t3Portal/resources/images/globals/header/headerbar.bg.blu.gif" '
           'style="width:100%; height:40px; margin:0px; border:0px; padding:0px">\n'
           '<div class="nav-link">\n']
    for title, link in manuals(root):
        out.append("<a href='/%s'>%s</a><br>\n" % (html.escape(link), title))
    out.append('</div>')
    fluids = fluid_pages(root)
    if fluids:
        out.append('<div class="nav-link"><br><b>Fluid Capacities</b><br>\n')
        for title, pages in fluids:
            out.append("%s:<br>\n" % html.escape(title, quote=False))
            for label, link in pages:
                out.append("&nbsp;&nbsp;<a href='%s'>%s</a><br>\n" % (html.escape(link), html.escape(label, quote=False)))
        out.append('</div>')
    if os.path.isdir(os.path.join(root, "PDFs")):
        out.append('<div class="nav-link"><br><a href="PDFs/index.html">PDF File Index</a></div>')
    out.append('</body>')
    sys.stdout.buffer.write("".join(out).encode("utf-8"))


if __name__ == "__main__":
    main()
