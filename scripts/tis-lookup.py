#!/usr/bin/env python3
#
# tis-lookup.py - Find a vehicle's manual codes from its make, model and year
#
# Asks for the make (division), model and year the way the TIS search page does, offering only what TIS
# has, then searches TIS's Service Information for that vehicle and prints the code of each manual:
#
#     Repair Manual           RM3900U
#     Wiring Diagrams         EM3900U
#     New Car Features        NM3900U
#     Body/Collision Repair   BM3900U
#
#     To download them:  tis-clone 3900U
#
# Most vehicles use one code for every manual; when a manual has a different one (ie: the 2013 Prius V's
# body repair manual is BM18M0U, the rest 23C0U), the command names it (tis-clone 23C0U --bm 18M0U).
#
# Usage:
#   tis-lookup.py                          ask for the make, model and year
#   tis-lookup.py LEXUS LX600 2024         no questions (any of them can be left off to be asked)
#   tis-lookup.py --args ...               print only the tis-clone arguments, ie: 23C0U --bm 18M0U
#
# Questions and messages go to stderr and the answer to stdout, so tis-clone can use --args.
# Uses the session tis-login.sh saved, and logs in again (after you press Enter) if it has expired.
#
# Exit status: 0 found, 1 no manuals found or no answer given, 75 the session expired and could not log in again.
#

import argparse
import collections
import html
import importlib.util
import os
import re
import sys

here = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location("tis_refsearch", os.path.join(here, "tis-refsearch.py"))
tis_refsearch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tis_refsearch)

DIVISIONS = ["LEXUS", "SCION", "TOYOTA"]
SEARCH = ("/t3Portal/appmanager/t3/ti?_nfpb=true&_windowLabel=repairform&repairform_actionOverride="
          "%2Fportlets%2Ftis%2Fdocument%2FsearchUplift%2Fform%2FsearchForm%2FsearchDocument&_pageLabel=t3_library_repair_search")
FIELD = "repairformwlw-select_key:{actionForm.%s}"
TAB = "/t3Portal/appmanager/t3/ti?_nfpb=true&_pageLabel=%s"
# tis-clone option, title, results tab, publication prefixes
SECTIONS = [
    ("rm", "Repair Manual", "lib_rm_page", ("RM",)),
    ("ewd", "Wiring Diagrams", "lib_ewd_page", ("EWD", "EM", "WD")),
    ("nm", "New Car Features", "lib_ncf_page", ("NCF", "NM")),
    ("bm", "Body/Collision Repair", "lib_cr_page", ("BM", "CR", "BR")),
]
PUB_RE = re.compile(r"publicationNumber=([A-Z]+)([0-9A-Z]{4,6})[&\"']")


def choose(what, options):
    """Ask the user to pick one of options, by number or name (any unique part of it)"""
    width = max(len(o) for o in options) + 6
    cols = max(1, 100 // width)
    rows = (len(options) + cols - 1) // cols
    print("\n%s:" % what)
    for r in range(rows):
        print("".join(("%3d. %s" % (i + 1, options[i])).ljust(width) for i in range(r, len(options), rows)).rstrip())
    while True:
        try:
            answer = input("%s (number or name): " % what).strip()
        except EOFError:
            print()
            sys.exit(1)
        # A name first: Toyota has a model called 86
        exact = [o for o in options if o.lower() == answer.lower()]
        if exact:
            return exact[0]
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        found = match(answer, options)
        if found:
            return found
        print("    Please pick one of the %d above" % len(options))


def match(answer, options):
    """The option answer names: exactly, or the only one starting with or containing it (any case)"""
    a = answer.lower()
    for test in (lambda o: o.lower() == a, lambda o: o.lower().startswith(a), lambda o: a in o.lower()):
        found = [o for o in options if test(o)]
        if found:
            return found[0] if len(found) == 1 else None
    return None


def codes(rs, division, model, year):
    """{section: Counter((prefix, code))} from a Service Information search and its result tabs"""
    data = {
        FIELD % "division" + "OldValue": "true", FIELD % "division": division,
        "repairform{actionForm.invoker}": "repair", "lastChanged": "", "lastModel": "", "lastYear": "",
        FIELD % "model": model, FIELD % "year": year,
        FIELD % "serviceCategory": "ALL", FIELD % "section": "ALL",
        "repairform{actionForm.keyword}": "", "repairform{actionForm.searchLanguage}": "en",
    }
    page = rs.request("POST", SEARCH, data)
    if "Technical Error" in page:
        raise tis_refsearch.SearchFailed("TIS couldn't search for %s %s %s" % (division, model, year))
    found = collections.OrderedDict()
    for option, title, tab, prefixes in SECTIONS:
        page = rs.request("GET", TAB % tab)
        found[option] = collections.Counter(pub for pub in PUB_RE.findall(html.unescape(page)) if pub[0] in prefixes)
    return found


def main():
    ap = argparse.ArgumentParser(description="Find a vehicle's manual codes from its make, model and year")
    ap.add_argument("vehicle", nargs="*", metavar="MAKE MODEL YEAR", help="ie: LEXUS LX600 2024 (anything left off is asked)")
    ap.add_argument("--args", action="store_true", help="print only the tis-clone arguments")
    ap.add_argument("--wait", type=float, default=1.0, help="seconds between requests (default 1)")
    args = ap.parse_args()
    if len(args.vehicle) > 3:
        ap.error("give at most MAKE MODEL YEAR")

    # Everything but the answer goes to stderr (including tis-fetch's re-login messages)
    answer_to = sys.stdout
    sys.stdout = sys.stderr

    cfg = tis_refsearch.tis_fetch.load_cfg()
    os.makedirs(cfg["DOWNLOAD_TO"], exist_ok=True)
    rs = tis_refsearch.RefSearch(cfg, args.wait)
    given = list(args.vehicle) + [None] * (3 - len(args.vehicle))

    def pick(what, value, options):
        if not options:
            print("TIS has no %s to choose from." % what.lower())
            sys.exit(1)
        if value is None:
            return choose(what, options)
        found = next((o for o in options if o.lower() == value.lower()), None)
        if not found:
            print("TIS has no %s %r.  The choices are: %s" % (what.lower(), value, ", ".join(options)))
            sys.exit(1)
        return found

    try:
        division = pick("Make", given[0], DIVISIONS)
        model = pick("Model", given[1], rs.vehicles("model", division))
        year = pick("Year", given[2], rs.vehicles("year", model, division))
        print("\nLooking up the %s %s %s manuals ..." % (year, division, model), flush=True)
        found = rs.retrying(codes, rs, division, model, year)
    except tis_refsearch.SearchFailed as e:
        print(e)
        return 1
    finally:
        rs.fetcher.save_cookies()

    best = {opt: c.most_common(1)[0][0][1] for opt, c in found.items() if c}
    if not best:
        print("TIS has no manuals for the %s %s %s." % (year, division, model))
        return 1
    main_code = best.get("rm") or collections.Counter(best.values()).most_common(1)[0][0]
    tis_args = [main_code] + ["--%s %s" % (opt, code) for opt, code in best.items() if code != main_code]

    out = sys.stderr if args.args else answer_to
    print(file=out)
    for option, title, tab, prefixes in SECTIONS:
        names = [prefix + code for (prefix, code), n in found[option].most_common()]
        print("    %-24s %s%s" % (title, names[0] if names else "none",
                                  "  (also: %s)" % ", ".join(names[1:]) if len(names) > 1 else ""), file=out)
    print("\nTo download them:  %s/tis-clone %s" % (os.path.dirname(cfg["SCRIPT_BASE"]), " ".join(tis_args)), file=out)
    print("Owner's manuals and other Reference Information:  %s/dl-ref.sh %s \"%s\" %s"
          % (cfg["SCRIPT_BASE"], division, model, year), file=out)
    if args.args:
        print(" ".join(tis_args), file=answer_to)
    return 0


if __name__ == "__main__":
    sys.exit(main())
