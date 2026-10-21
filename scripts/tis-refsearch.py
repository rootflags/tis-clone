#!/usr/bin/env python3
#
# tis-refsearch.py - Search TIS's Reference Information for a vehicle
#
# Runs the Reference Information search (TIS > Library > Reference Information) for a division, model and
# year, in each document group, and lists what it finds:
#   Technician    dealer model reference, emergency response guides, VIN decoder charts, technical references
#   Warranty      "Warranty & Claim Processing": the older (to about 2015) Flat Rate Manuals
#   Owner, Service Operations/Parts, Canada Technician/Service
# Newer vehicles' Flat Rate Manual is a separate TIS application and isn't found here.
#
# Results are documents on their own (ie: tr/L-TR-0122-D, a VIN decoder chart) or pages of a publication
# (ie: frm/FM18X0U, the 2013 Land Cruiser Flat Rate Manual).  Some publications cover every vehicle (ie:
# asm/ASM001 has 1,268 pages), so only the pages the search found are kept.  --toc writes a toc.xml listing
# them all (group > publication or document type > document), so dl-ref.sh can download them and they can
# be browsed like a manual.
#
# Uses the session tis-login.sh saved, and logs in again (after you press Enter) if it has expired.
#
# Usage:
#   tis-refsearch.py DIVISION MODEL YEAR [-g GROUP ...]     ie: tis-refsearch.py LEXUS LX600 2024
#       YEAR can be a range (2022-2027) or ALL.  GROUP: technician, warranty, owner, serviceops, canada
#       (default: all of them).  --tsv prints one tab separated line per document instead.
#   tis-refsearch.py ... --toc toc.xml                      also write the toc.xml
#   tis-refsearch.py --models DIVISION                      the models TIS knows, ie: LX600, LAND CRUISER
#   tis-refsearch.py --years DIVISION                       the model years TIS knows
#
# Exit status: 0 done, 1 a search failed, 75 the session expired and could not log in again.
#

import argparse
import collections
import html
import importlib.util
import os
import re
import sys
import time
import urllib.parse
from xml.sax.saxutils import escape, quoteattr

from tislog import tee_to_log

here = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location("tis_fetch", os.path.join(here, "tis-fetch.py"))
tis_fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tis_fetch)

GROUPS = collections.OrderedDict([
    ("technician", "Technician"),
    ("warranty", "Warranty"),
    ("owner", "Owner"),
    ("serviceops", "Service Operations"),
    ("canada", "Canada Technician/Service"),
])
GROUP_TITLES = {"Technician": "Technician", "Warranty": "Warranty & Claim Processing", "Owner": "Owner",
                "Service Operations": "Service Operations/Parts", "Canada Technician/Service": "Canada Technician/Service"}
# Document types (objType) seen so far; others are shown by their code
TYPES = {"frm": "Flat Rate Manual", "dmr": "Dealer Model Reference", "erg": "Emergency Response Guide",
         "tr": "Technical Reference", "asm": "ASM/Parts Reference", "om-s": "Owner's Manual",
         "omms-s": "Warranty and Maintenance", "omnav-s": "Navigation, Multimedia and Accessories"}

REFPAGE = "/t3Portal/appmanager/t3/ti?_nfpb=true&_pageLabel=tis_lib_ref_page"
SEARCH = ("/t3Portal/appmanager/t3/ti?_nfpb=true&_windowLabel=ReferenceForm_1&ReferenceForm_1_actionOverride="
          "%2Fportlets%2Ftis%2Fdocument%2FsearchUplift%2Fform%2FsearchForm%2FsearchDocument&_pageLabel=t3_page_66")
VEHICLES = "/t3Portal/ajax/getVehicle.jsp?dataset=%s&key=%s&target=x&addAll=true&prefix=true&formTagId=x&isFireTarget="
FIELD = "ReferenceForm_1wlw-select_key:{actionForm.%s}"

COUNT_RE = re.compile(r"writeResultsOnTitleBar\(\s*\d+\s*,\s*'[^']*'\s*\+\s*(\d+)")
ROW_RE = re.compile(r'<td style="vertical-align:top;\s*width:25px;">\s*\d+\.\s*</td>(.*?)</tr>', re.S)
LINK_RE = re.compile(r'<a href="([^"]+)"[^>]*>(.*?)</a>', re.S)
# A results page can hold more than one list (each its own portlet window), and each has its own pages
NEXT_RE = re.compile(r'<a href="([^"]*_windowLabel=([^&"]+)[^"]*searchResult%2FgoNext[^"]*)"')
KEYS_RE = re.compile(r'\["([^"]*)","([^"]*)"\]')


class SearchFailed(Exception):
    pass


class RefSearch:
    def __init__(self, cfg, wait):
        args = argparse.Namespace(manifest=None, insecure=False, no_relogin=False, quiet=True, scope="/t3Portal/",
                                  wait=wait, requisites=False, base=None)
        self.fetcher = tis_fetch.Fetcher(cfg, args)
        self.site = cfg["WEBSITE"]
        self.wait = wait

    def request(self, method, path, data=None):
        """GET or POST with the TIS session.  Raises tis_fetch.SessionDead if TIS sent its login page"""
        time.sleep(self.wait)
        f = self.fetcher
        for delay in (5, 15, 45, None):
            try:
                r = f.http.request(method, urllib.parse.urljoin(self.site, path), data=data, timeout=(20, 120),
                                   headers={"Referer": self.site + REFPAGE})
                if r.status_code < 500:
                    break
                err = "HTTP %d" % r.status_code
            except tis_fetch.requests.RequestException as e:
                err = type(e).__name__
            if delay is None:
                raise SearchFailed(err)
            print("    %s, retrying in %ds" % (err, delay), flush=True)
            time.sleep(delay)
        f.since_cookie_save += 1
        if f.login_redirect(r) or tis_fetch.LOGIN_BODY_RE.search(r.content[:200000]) or r.status_code in (401, 403):
            raise tis_fetch.SessionDead()
        if r.status_code != 200:
            raise SearchFailed("HTTP %d" % r.status_code)
        return r.text

    def retrying(self, what, *a):
        """Run what(*a), logging in again and starting over if the session dies"""
        while True:
            try:
                return what(*a)
            except tis_fetch.SessionDead:
                f = self.fetcher
                if f.session_ok():
                    raise SearchFailed("TIS refused the request although the session works")
                if not f.relogin():
                    sys.exit(tis_fetch.EXIT_SESSION)

    def vehicles(self, dataset, division):
        text = self.retrying(self.request, "GET", VEHICLES % (dataset, urllib.parse.quote(division)))
        return [v for v, label in KEYS_RE.findall(text) if v != "ALL"]

    def search(self, division, model, year, group):
        """[result dict] for one search, following its "next" pages"""
        data = {
            FIELD % "division" + "OldValue": "true", FIELD % "division": division,
            "ReferenceForm_1{actionForm.invoker}": "reference", "lastChanged": "", "lastModel": "", "lastYear": "",
            FIELD % "model": model, FIELD % "year": year,
            FIELD % "docGroup" + "OldValue": "true", FIELD % "docGroup": group,
            "ReferenceForm_1{actionForm.keyword}": "", "ReferenceForm_1{actionForm.searchLanguage}": "en",
        }
        page = self.request("POST", SEARCH, data)
        results = collections.OrderedDict()
        total = None
        following = None                        # the list whose next page we asked for
        links = {}                              # each list's "next" link (TIS keeps the place in the session)
        for _ in range(500):
            if "Technical Error" in page:
                m = re.search(r"MESSAGE:\s*(.*?)(?:\sat\s|$)", html.unescape(re.sub(r"<[^>]+>", " ", page)), re.S)
                raise SearchFailed("TIS error: %s" % (m.group(1).strip()[:200] if m else "unknown"))
            if total is None:
                total = sum(int(n) for n in COUNT_RE.findall(page))
            body = re.sub(r"<!--.*?-->", "", page, flags=re.S)
            for row in ROW_RE.findall(body):
                link = LINK_RE.search(row)
                if link:
                    r = result(html.unescape(link.group(1)), html.unescape(re.sub(r"<[^>]+>|\s+", " ", link.group(2))).strip())
                    results.setdefault(r["path"], r)
            nexts = collections.OrderedDict((label, url) for url, label in NEXT_RE.findall(body))
            links.update(nexts)
            if following is None:
                todo = list(nexts)              # every list that has more pages
            elif following not in nexts:
                todo.remove(following)          # that list is done
            if not todo or len(results) >= total:
                break
            following = todo[0]
            # The links say techinfo.toyota.com:443; keep to the site as configured (a different host looks like
            # a redirect to the login page)
            u = urllib.parse.urlsplit(html.unescape(links[following]))
            page = self.request("GET", u.path + "?" + u.query)
        if len(results) != total:
            print("    (TIS said %d results, %d were listed)" % (total, len(results)), flush=True)
        return list(results.values())


def result(link, title):
    """What a search result link points at.  path is the document's /t3Portal/document/... page, pub the
    publication folder (type/number), toc whether that publication has its own toc.xml"""
    u = urllib.parse.urlsplit(link)
    q = dict(urllib.parse.parse_qsl(u.query))
    r = {"title": title, "type": q.get("objType", ""), "link": link}
    if "siviewer/index.jsp" in u.path and q.get("href"):
        if q.get("dir"):
            r.update(path="/t3Portal/document/%s/%s" % (q["dir"], q["href"]), pub=q["dir"], toc=True)
        else:
            parts = q["href"].split("/")
            r.update(path="/t3Portal/document/" + q["href"], pub="/".join(parts[:2]), toc=False)
            r["type"] = r["type"] or parts[0]
    else:
        r.update(path=u.path, pub="", toc=False)
    return r


def years_of(spec):
    m = re.match(r"^(\d{4})-(\d{4})$", spec)
    if m:
        return [str(y) for y in range(int(m.group(1)), int(m.group(2)) + 1)]
    return [spec]


def section(r):
    """The toc.xml section a result goes in: its publication, or for a document on its own, its type"""
    kind = TYPES.get(r["type"], r["type"].upper() or "Other")
    if r["toc"]:
        return "%s: %s (%s)" % (kind, r["title"].split(":")[0].strip(), r["pub"].split("/")[-1])
    return kind


def write_toc(path, title, found, search):
    """A toc.xml (the same layout as TIS's) of everything found: group > publication or type > document"""
    tree = collections.OrderedDict()
    for group, results in found.items():
        for r in results:
            if r["path"].startswith("/t3Portal/document/"):
                tree.setdefault(GROUP_TITLES[group], collections.OrderedDict()).setdefault(section(r), []).append(r)
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n<!-- Made by tis-refsearch.py from a TIS Reference Information search -->\n'
           "<xmltoc refsearch=%s>\n  <name>%s</name>\n" % (quoteattr("|".join(search)), escape(title))]
    for group, kinds in tree.items():
        out.append('  <item href="">\n    <name>%s</name>\n' % escape(group))
        for kind, results in kinds.items():
            out.append('    <item href="">\n      <name>%s</name>\n' % escape(kind))
            for r in results:
                out.append("      <item href=%s>\n        <name>%s</name>\n      </item>\n" % (quoteattr(r["path"]), escape(r["title"])))
            out.append("    </item>\n")
        out.append("  </item>\n")
    out.append("</xmltoc>\n")
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("".join(out))
    os.replace(tmp, path)
    return sum(len(r) for k in tree.values() for r in k.values())


def main():
    ap = argparse.ArgumentParser(description="Search TIS's Reference Information for a vehicle")
    ap.add_argument("vehicle", nargs="*", metavar="DIVISION MODEL YEAR", help="ie: LEXUS LX600 2024 (YEAR: 2024, 2022-2027 or ALL)")
    ap.add_argument("-g", "--group", action="append", choices=list(GROUPS), help="document group (default: all)")
    ap.add_argument("--tsv", action="store_true", help="one tab separated line per document: group, type, publication, path, title")
    ap.add_argument("--toc", metavar="FILE", help="write a toc.xml of the documents that don't have their own")
    ap.add_argument("--title", help="title for the --toc file (default: DIVISION YEAR MODEL Reference Information)")
    ap.add_argument("--models", metavar="DIVISION", help="list the models TIS knows for a division")
    ap.add_argument("--years", metavar="DIVISION", help="list the model years TIS knows for a division")
    ap.add_argument("--wait", type=float, default=1.0, help="seconds between requests (default 1)")
    args = ap.parse_args()

    cfg = tis_fetch.load_cfg()
    tee_to_log(cfg)
    os.makedirs(cfg["DOWNLOAD_TO"], exist_ok=True)
    rs = RefSearch(cfg, args.wait)

    if args.models or args.years:
        for v in rs.vehicles("model" if args.models else "yearreverse", (args.models or args.years).upper()):
            print(v)
        rs.fetcher.save_cookies()
        return 0
    if len(args.vehicle) != 3:
        ap.error("give DIVISION MODEL YEAR, ie: LEXUS LX600 2024 (quote a model with a space: \"LAND CRUISER\")")
    division, model, year = args.vehicle[0].upper(), args.vehicle[1], args.vehicle[2].upper()
    # TIS's spelling of the model (Toyota's are mixed case, ie: Land Cruiser)
    models = rs.vehicles("model", division)
    match = [m for m in models if m.lower() == model.lower()]
    if not match:
        near = [m for m in models if model.lower() in m.lower() or m.lower() in model.lower()]
        print("TIS has no %s model %s.  %s" % (division, model, "Did you mean: %s?" % ", ".join(near) if near else
              "tis-refsearch.py --models %s lists them." % division))
        return 1
    model = match[0]

    found = collections.OrderedDict()
    rc = 0
    for g in args.group or list(GROUPS):
        group = GROUPS[g]
        seen = set()
        found[group] = []
        for y in years_of(year):
            if not args.tsv:
                print("Searching %s %s %s, %s ..." % (division, model, y, GROUP_TITLES[group]), flush=True)
            try:
                results = rs.retrying(rs.search, division, model, y, group)
            except SearchFailed as e:
                print("    search failed: %s" % e, flush=True)
                rc = 1
                continue
            for r in results:
                if r["path"] not in seen:
                    seen.add(r["path"])
                    found[group].append(r)
    rs.fetcher.save_cookies()

    pubs = collections.OrderedDict()            # publication -> its pages that were found
    for group, results in found.items():
        for r in results:
            if r["toc"]:
                pubs.setdefault(r["pub"], []).append(r)
        if args.tsv:
            for r in results:
                print("\t".join([group, r["type"], r["pub"], r["path"], r["title"]]))
            continue
        print("\n%s: %d document%s" % (GROUP_TITLES[group], len(results), "" if len(results) == 1 else "s"))
        for r in results:
            if not r["toc"]:
                print("    %-48s %s" % (r["path"].replace("/t3Portal/document/", ""), r["title"]))
        for pub in collections.OrderedDict.fromkeys(r["pub"] for r in results if r["toc"]):
            print("    %-48s %s (%d pages)" % (pub + "/", section(pubs[pub][0]), len(pubs[pub])))

    if args.toc:
        title = args.title or "%s %s %s Reference Information" % (division, year, model)
        n = write_toc(args.toc, title, found, (division, model, year))
        if not args.tsv:
            print("\nWrote %s (%d documents)" % (args.toc, n))
    return rc


if __name__ == "__main__":
    sys.exit(main())
