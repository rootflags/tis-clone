#!/usr/bin/env python3
#
# toc2html.py - Make a manual's navigation page (toc.html) from its toc.xml
#
# The page is a collapsible Bootstrap menu, three or four levels deep, whose links open each document in
# the manual_frame of the manual's index.html.  dl-html-inc.sh runs this after every download.  Line 2 of
# the output is the manual's title, which build-index.py lists on the front page.
#
# Usage:
#   toc2html.py toc.xml > toc.html
#

import html
import sys
import xml.etree.ElementTree as ET


def name(node):
    return node.findtext("name") or ""


def text(s):
    """Link text: TIS pads names with no-break spaces, ie: [12/2012 - \xa0\xa0\xa0]"""
    return html.escape(s.replace("\xa0", " "), quote=False)


def category(node):
    n = name(node)
    return "Body" if n == "body" else n


def read_nav(root):
    """{section: {subsection: {"items": [(name, href)], "groups": {group: [(name, href)]}}}}"""
    nav = {}
    for entry in root.findall("item"):
        for tk in entry.findall("item"):
            for sk in tk.findall("item"):
                if sk.get("href"):
                    sub = nav.setdefault(name(entry), {}).setdefault(category(tk), {"items": [], "groups": {}})
                    sub["items"].append((name(sk), sk.get("href")))
                else:
                    for nk in sk.findall("item"):
                        sub = nav.setdefault(name(entry), {}).setdefault(category(tk), {"items": [], "groups": {}})
                        sub["groups"].setdefault(category(sk), []).append((name(nk), nk.get("href", "")))
    return nav


def links(items, indent, pad):
    out = []
    for item, href in sorted(items, key=lambda i: i[0]):
        out.append("%s<li class='nav-item' style='padding:0px 0px 0px %dpx;'><a class='nav-link' target='manual_frame' href='%s'>\n"
                   % (indent, pad, html.escape(href)))
        out.append("%s<i class='fa fa-fw fa-clock-o'></i>%s</a></li>\n" % (indent, text(item)))
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit("Syntax: %s toc.xml > toc.html" % sys.argv[0])
    try:
        root = ET.parse(sys.argv[1]).getroot()
    except (OSError, ET.ParseError) as e:
        sys.exit("%s: can't read %s: %s" % (sys.argv[0], sys.argv[1], e))
    topic = html.escape(name(root), quote=False)
    nav = read_nav(root)

    out = ['<!DOCTYPE html><html><head><title>\n%s\n</title>\n' % topic,
           '    <meta charset="utf-8">\n',
           '    <meta name="viewport" content="width=device-width">\n',
           '    <link rel="stylesheet" href="/framework/bootstrap.min.css">\n',
           '  </head>\n',
           '  <body>\n',
           # Back to the front page (build-index.py's), out of the manual's frames
           '<a class="nav-link" href="/index.html" target="_top">&lt; Home</a>\n',
           '\n',
           ' <ul class="nav flex-column flex-nowrap"><b>%s</b>\n' % topic,
           "  <ul class='nav flex-column flex-nowrap'>\n"]
    sub1 = sub2 = sub3 = 0
    for topkey in sorted(nav):
        sub1 += 1
        out.append("    <li class='nav-item drop'>\n")
        out.append("    <a class='nav-link collapsed' href='#submenu%d' data-toggle='collapse' >+ %s</a>\n"
                   % (sub1, html.escape(topkey, quote=False)))
        out.append("    <div class='collapse' id='submenu%d' aria-expanded='false'>\n" % sub1)
        out.append("    <ul class='flex-column nav' style='padding:0px 0px 0px 40px;'>\n")
        for subkey in sorted(nav[topkey]):
            sub2 += 1
            sub = nav[topkey][subkey]
            menu = "submenu%dsub%d" % (sub1, sub2)
            out.append("      <li class='nav-item'><a class='nav-link collapsed py-0' href='#%s' data-toggle='collapse'>- %s</a></li>\n"
                       % (menu, html.escape(subkey, quote=False)))
            out.append("      <div class='collapse' id='%s' aria-expanded='false'>\n" % menu)
            out.append("      <ul class='flex-column nav'>\n")
            out += links(sub["items"], "        ", 80)
            for nxtkey in sorted(sub["groups"]):
                sub3 += 1
                out.append("        <li class='nav-item'><a class='nav-link collapsed py-1'  data-toggle='collapse' href='#%ssub%d' style='padding:0px 0px 0px 50px;'>\n"
                           % (menu, sub3))
                out.append("        <i class='fa fa-fw fa-clock-o'></i>%s</a>\n" % html.escape(nxtkey, quote=False))
                out.append("        <div class='collapse' id='%ssub%d' aria-expanded='false'>\n" % (menu, sub3))
                out.append("        <ul class='flex-column nav'>\n")
                out += links(sub["groups"][nxtkey], "          ", 80)
                out.append("        </ul></div></li>\n")
            out.append("      </ul></div></li>\n")
        out.append("    </ul></div>\n")
    out.append("  </ul>\n")
    out.append('\n<script src="/framework/jquery-3.4.1.min.js"></script>\n'
               '<script src="/framework/popper.min.js"></script>\n'
               '<script src="/framework/bootstrap.min.js"></script>\n'
               '</body>')
    sys.stdout.buffer.write("".join(out).encode("utf-8"))


if __name__ == "__main__":
    main()
