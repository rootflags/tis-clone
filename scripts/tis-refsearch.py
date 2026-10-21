#!/usr/bin/env python3
#
# tis-refsearch.py - Search TIS's Reference Information for a vehicle
#
# Runs the Reference Information search (TIS > Library > Reference Information) for a division, model and
# year, in each document group, and lists what it finds:
#   Technician    dealer model reference, emergency response guides, VIN decoder charts, technical references
#   Warranty      "Warranty & Claim Processing": the older (to about 2015) Flat Rate Manuals
#   Owner, Service Operations/Parts, Canada Technician/Service
# Newer vehicles' Flat Rate Manual is a separate TIS application (tis-frm.py).
#
# It can also list what the Service Information search (TIS > Library) has for the vehicle in two of its
# result tabs, which dl-bulletins.sh downloads:
#   bulletins     the SB/TT tab's "Service Bulletin" and "Tech Tip" lists (USA; the Canada and Mexico lists
#                 are left out), without the bulletins marked Obsolete
#   campaigns     the SC tab: service campaigns and safety recalls (dealer letter and technical instructions)
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
#       YEAR can be a range (2022-2027), a list (2022,2024-2025) or ALL.  GROUP: technician, warranty, owner,
#       serviceops, canada (the default: all of those), bulletins, campaigns.  --tsv prints one tab separated
#       line per document instead.
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
# Service Information search result tabs: group -> (tab page, list titles to keep or None for all, skip obsolete)
SI_GROUPS = collections.OrderedDict([
    ("bulletins", ("lib_tsb_page", ("Service Bulletin", "Tech Tip"), True)),
    ("campaigns", ("lib_cp_page", None, False)),
])
GROUP_TITLES = {"Technician": "Technician", "Warranty": "Warranty & Claim Processing", "Owner": "Owner",
                "Service Operations": "Service Operations/Parts", "Canada Technician/Service": "Canada Technician/Service",
                "bulletins": "Service Bulletins and Tech Tips", "campaigns": "Service Campaigns"}
# Document types (objType) seen so far; others are shown by their code
TYPES = {"frm": "Flat Rate Manual", "dmr": "Dealer Model Reference", "erg": "Emergency Response Guide",
         "tr": "Technical Reference", "asm": "ASM/Parts Reference", "om-s": "Owner's Manual",
         "omms-s": "Warranty and Maintenance", "omnav-s": "Navigation, Multimedia and Accessories",
         "sb": "Service Bulletin", "sb-usa-tdm": "Service Bulletin", "tt": "Tech Tip", "cp": "Service Campaign"}

REFPAGE = "/t3Portal/appmanager/t3/ti?_nfpb=true&_pageLabel=tis_lib_ref_page"
SEARCH = ("/t3Portal/appmanager/t3/ti?_nfpb=true&_windowLabel=ReferenceForm_1&ReferenceForm_1_actionOverride="
          "%2Fportlets%2Ftis%2Fdocument%2FsearchUplift%2Fform%2FsearchForm%2FsearchDocument&_pageLabel=t3_page_66")
VEHICLES = "/t3Portal/ajax/getVehicle.jsp?dataset=%s&key=%s&target=x&addAll=true&prefix=true&formTagId=x&isFireTarget="
FIELD = "ReferenceForm_1wlw-select_key:{actionForm.%s}"
# The Service Information search (also used by tis-lookup.py); its results stay in the session, by tab
SI_SEARCH = ("/t3Portal/appmanager/t3/ti?_nfpb=true&_windowLabel=repairform&repairform_actionOverride="
             "%2Fportlets%2Ftis%2Fdocument%2FsearchUplift%2Fform%2FsearchForm%2FsearchDocument&_pageLabel=t3_library_repair_search")
SI_FIELD = "repairformwlw-select_key:{actionForm.%s}"
TAB = "/t3Portal/appmanager/t3/ti?_nfpb=true&_pageLabel=%s"

COUNT_RE = re.compile(r"writeResultsOnTitleBar\(\s*\d+\s*,\s*'[^']*'\s*\+\s*(\d+)")
ROW_RE = re.compile(r'<td style="vertical-align:top;\s*width:25px;">\s*\d+\.\s*</td>(.*?)</tr>', re.S)
LINK_RE = re.compile(r'<a href="([^"]+)"[^>]*>(.*?)</a>', re.S)
# A results page can hold more than one list (each its own portlet window), and each has its own pages
NEXT_RE = re.compile(r'<a href="([^"]*_windowLabel=([^&"]+)[^"]*searchResult%2FgoNext[^"]*)"')
KEYS_RE = re.compile(r'\["([^"]*)","([^"]*)"\]')
LIST_TITLE_RE = re.compile(r'<td class="bea-portal-details-window-titlebar-title">(.*?)</td>', re.S)
OBSOLETE_RE = re.compile(r"\bobsolete\W*$", re.I)


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

    def vehicles(self, dataset, key, division=None):
        """TIS's lists for the vehicle dropdowns: dataset "model" (key: division), "yearreverse" (key: division,
        every year) or "year" (key: model, also give its division)"""
        path = VEHICLES % (dataset, urllib.parse.quote(key))
        if division:
            path += "&division=" + urllib.parse.quote(division)
        text = self.retrying(self.request, "GET", path)
        return [v for v, label in KEYS_RE.findall(text) if v != "ALL"]

    def search(self, division, model, year, group):
        """[result dict] for one Reference Information search, following its "next" pages"""
        data = {
            FIELD % "division" + "OldValue": "true", FIELD % "division": division,
            "ReferenceForm_1{actionForm.invoker}": "reference", "lastChanged": "", "lastModel": "", "lastYear": "",
            FIELD % "model": model, FIELD % "year": year,
            FIELD % "docGroup" + "OldValue": "true", FIELD % "docGroup": group,
            "ReferenceForm_1{actionForm.keyword}": "", "ReferenceForm_1{actionForm.searchLanguage}": "en",
        }
        return self.collect(self.request("POST", SEARCH, data), None)

    def si_search(self, division, model, year):
        """Run the Service Information search; its result tabs can then be read (TAB) in the same session"""
        data = {
            SI_FIELD % "division" + "OldValue": "true", SI_FIELD % "division": division,
            "repairform{actionForm.invoker}": "repair", "lastChanged": "", "lastModel": "", "lastYear": "",
            SI_FIELD % "model": model, SI_FIELD % "year": year,
            SI_FIELD % "serviceCategory": "ALL", SI_FIELD % "section": "ALL",
            "repairform{actionForm.keyword}": "", "repairform{actionForm.searchLanguage}": "en",
        }
        page = self.request("POST", SI_SEARCH, data)
        if "Technical Error" in page:
            raise SearchFailed("TIS couldn't search for %s %s %s" % (division, model, year))

    def tab_search(self, division, model, year, group):
        """[result dict] in one Service Information result tab (SI_GROUPS), following its "next" pages"""
        tab, wanted, skip_obsolete = SI_GROUPS[group]
        self.si_search(division, model, year)
        results = self.collect(self.request("GET", TAB % tab), wanted)
        return [r for r in results if not (skip_obsolete and OBSOLETE_RE.search(r["title"]))]

    def collect(self, page, wanted):
        """The results in a results page and its next pages: of every list, or of the lists titled wanted"""
        results = collections.OrderedDict()
        total = None
        following = None                        # the list whose next page we asked for
        links = {}                              # each list's "next" link (TIS keeps the place in the session)
        for _ in range(500):
            if "Technical Error" in page:
                m = re.search(r"MESSAGE:\s*(.*?)(?:\sat\s|$)", html.unescape(re.sub(r"<[^>]+>", " ", page)), re.S)
                raise SearchFailed("TIS error: %s" % (m.group(1).strip()[:200] if m else "unknown"))
            body = re.sub(r"<!--.*?-->", "", page, flags=re.S)
            lists = [part for part in result_lists(body) if wanted is None or part[0] in wanted]
            if total is None:
                total = sum(int(n) for title, part in lists for n in COUNT_RE.findall(part))
            nexts = collections.OrderedDict()
            for title, part in lists:
                for row in ROW_RE.findall(part):
                    link = LINK_RE.search(row)
                    if link:
                        r = result(html.unescape(link.group(1)), html.unescape(re.sub(r"<[^>]+>|\s+", " ", link.group(2))).strip())
                        results.setdefault(r["path"], r)
                nexts.update((label, url) for url, label in NEXT_RE.findall(part))
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


def result_lists(body):
    """[(title, part of the page)] for each titled window on a results page (ie: Service Bulletin, Tech Tip)"""
    found = [(m.start(), html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(1))).strip()) for m in LIST_TITLE_RE.finditer(body)]
    if not found:
        return [("", body)]
    parts = [("", body[:found[0][0]])]
    for i, (pos, title) in enumerate(found):
        parts.append((title, body[pos:found[i + 1][0] if i + 1 < len(found) else len(body)]))
    return parts


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
    """The years in 2024, 2022-2027, 2022,2024-2025 or ALL (which TIS searches as one)"""
    years = []
    for part in spec.split(","):
        m = re.match(r"^(\d{4})-(\d{4})$", part.strip())
        found = [str(y) for y in range(int(m.group(1)), int(m.group(2)) + 1)] if m else [part.strip()]
        years += [y for y in found if y and y not in years]
    return years


def section(r):
    """The toc.xml section a result goes in: its publication, or for a document on its own, its type"""
    kind = TYPES.get(r["type"], r["type"].upper() or "Other")
    if r["type"] == "cp":
        # One section per campaign: "Safety Recall 24LA02 (Remedy Notice): 2022-2024 LX600; ... (Dealer Letter)" and
        # "SAFETY RECALL 24LA02; ... (Technical Instructions)" both go in "Safety Recall 24LA02"
        m = re.match(r"^(.*?)\b(\d\d[A-Z]{2}\d\d)\b", r["title"])
        if m:
            words = " ".join(re.sub(r"\([^)]*\)", " ", m.group(1)).split())     # "Safety (Noncompliance) Recall"
            return "%s %s" % (words.title() if words.isupper() else words, m.group(2))
        return r["title"].split(":")[0].strip()
    if r["toc"]:
        return "%s: %s (%s)" % (kind, r["title"].split(":")[0].strip(), r["pub"].split("/")[-1])
    return kind


def write_toc(path, title, found, search, rerun):
    """A toc.xml (the same layout as TIS's) of everything found: group > publication or type > document"""
    tree = collections.OrderedDict()
    for group, results in found.items():
        for r in results:
            if r["path"].startswith("/t3Portal/document/"):
                tree.setdefault(GROUP_TITLES[group], collections.OrderedDict()).setdefault(section(r), []).append(r)
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n<!-- Made by tis-refsearch.py from a TIS Reference Information search -->\n'
           "<xmltoc refsearch=%s rerun=%s>\n  <name>%s</name>\n" % (quoteattr("|".join(search)), quoteattr(rerun), escape(title))]
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
    ap.add_argument("vehicle", nargs="*", metavar="DIVISION MODEL YEAR", help="ie: LEXUS LX600 2024 (YEAR: 2024, 2022-2027, 2022,2024 or ALL)")
    ap.add_argument("-g", "--group", action="append", choices=list(GROUPS) + list(SI_GROUPS),
                    help="document group (default: all the Reference Information ones)")
    ap.add_argument("--tsv", action="store_true", help="one tab separated line per document: group, type, publication, path, title")
    ap.add_argument("--toc", metavar="FILE", help="write a toc.xml of the documents that don't have their own")
    ap.add_argument("--title", help="title for the --toc file (default: DIVISION YEAR MODEL WHAT)")
    ap.add_argument("--what", default="Reference Information", help="what the --toc file is, for its title (default: Reference Information)")
    ap.add_argument("--rerun", default="dl-ref.sh", help="the script that remakes the --toc folder, for tis-report.py (default dl-ref.sh)")
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
        group = GROUPS.get(g, g)
        seen = set()
        found[group] = []
        for y in years_of(year):
            if not args.tsv:
                print("Searching %s %s %s, %s ..." % (division, model, y, GROUP_TITLES[group]), flush=True)
            try:
                if g in SI_GROUPS:
                    results = rs.retrying(rs.tab_search, division, model, y, g)
                else:
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
        title = args.title or "%s %s %s %s" % (division, year, model, args.what)
        n = write_toc(args.toc, title, found, (division, model, year), args.rerun)
        if not args.tsv:
            print("\nWrote %s (%d documents)" % (args.toc, n))
    return rc


if __name__ == "__main__":
    sys.exit(main())
