#!/usr/bin/env python3
#
# build-index.py - Print the front page (index.html) listing every downloaded manual
#
# Lists each manual's toc.html (made by toc2html.py) and each wiring diagram's termdata.xml, sorted by
# title, plus a link to PDFs/index.html if there are PDFs.  tis-clone runs it after downloading.
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
    if os.path.isdir(os.path.join(root, "PDFs")):
        out.append('<div class="nav-link"><br><a href="PDFs/index.html">PDF File Index</a></div>')
    out.append('</body>')
    sys.stdout.buffer.write("".join(out).encode("utf-8"))


if __name__ == "__main__":
    main()
