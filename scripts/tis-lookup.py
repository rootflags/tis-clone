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
#     To download them:  tis-clone 3900U --ref LEXUS:LX600:2024
#
# Most vehicles use one code for every manual; when a manual has a different one (ie: the 2013 Prius V's
# body repair manual is BM18M0U, the rest 23C0U), the command names it (tis-clone 23C0U --bm 18M0U).
# --ref also downloads the vehicle's Reference Information (owner's manuals, ...; see dl-ref.sh).
#
# Usage:
#   tis-lookup.py                          ask for the make, model and year
#   tis-lookup.py LEXUS LX600 2024         no questions (any of them can be left off to be asked)
#   tis-lookup.py --args ...               print only the tis-clone arguments, ie:
#                                              23C0U --bm 18M0U --ref TOYOTA:Prius_V:2013
#   tis-lookup.py --ref-for TOC.XML        read which vehicle a downloaded manual is for, ask for the model
#                                          year (and the model, if the manual covers several) and print the
#                                          --ref value, ie: LEXUS:LX600:2024 (nothing if the user skips it).
#                                          tis-clone uses this when given a code without --ref.
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
import xml.etree.ElementTree as ET

here = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location("tis_refsearch", os.path.join(here, "tis-refsearch.py"))
tis_refsearch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tis_refsearch)

DIVISIONS = ["LEXUS", "SCION", "TOYOTA"]
TAB = tis_refsearch.TAB
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
    rs.si_search(division, model, year)
    found = collections.OrderedDict()
    for option, title, tab, prefixes in SECTIONS:
        page = rs.request("GET", TAB % tab)
        found[option] = collections.Counter(pub for pub in PUB_RE.findall(html.unescape(page)) if pub[0] in prefixes)
    return found


def vehicle_of(toc, rs):
    """(division, [models], first year, last year) a manual's toc.xml is for, or None.  Newer tocs list the
    models (<tocmodelname>) and years (<yeardata model-year=>); older ones only have the title, ie: "Toyota
    2013 Land Cruiser Repair Manual (RM18X0U)", whose model part is matched against TIS's model list"""
    try:
        root = ET.parse(toc).getroot()
    except (OSError, ET.ParseError):
        return None
    title = (root.findtext("name") or root.findtext("pubtitle") or "").strip()
    words = title.split()
    if not words or words[0].upper() not in DIVISIONS:
        return None
    division = words[0].upper()
    years = sorted(int(y.get("model-year")) for y in root.iter("yeardata") if (y.get("model-year") or "").isdigit())
    m = re.search(r"\b((?:19|20)\d\d)(?:\s*-\s*((?:19|20)\d\d))?\b(.*?)\s+(?:Repair|Collision|Body|New Car|Electrical|Wiring)", title)
    if not years and m:
        years = [int(m.group(1)), int(m.group(2) or m.group(1))]
    if not years:
        return None
    known = rs.vehicles("model", division)
    by_name = {k.lower(): k for k in known}
    models = []
    for n, _ in collections.Counter((t.text or "").strip() for t in root.iter("tocmodelname")).most_common():
        if n.lower() in by_name and by_name[n.lower()] not in models:
            models.append(by_name[n.lower()])
    if not models and m:
        # "LX600 LX700H" is two models, "Land Cruiser" one: take the longest known name at each word
        rest = m.group(3).split()
        while rest:
            for n in range(len(rest), 0, -1):
                name = " ".join(rest[:n]).lower()
                if name in by_name:
                    models.append(by_name[name])
                    rest = rest[n:]
                    break
            else:
                rest = rest[1:]
    return (division, models, years[0], years[-1]) if models else None


def ask_ref(toc, rs):
    """Ask for the model year (and model) of the vehicle toc is for.  Returns MAKE:MODEL:YEAR or None"""
    found = vehicle_of(toc, rs)
    if not found:
        print("Couldn't tell which vehicle %s is for, so no Reference Information." % toc)
        return None
    division, models, first, last = found
    span = str(first) if first == last else "%d-%d" % (first, last)
    print("\nThis manual is for the %s %s %s." % (span, division, " and ".join(models)))
    print("Its Reference Information (owner's, navigation and accessory manuals, maintenance guide, ...) is per model year.")
    model = models[0] if len(models) == 1 else choose("Which model", models)
    years = rs.vehicles("year", model, division)
    print("Give a year (2024), several (2022,2024), a range (2022-2024) or all (%s)." % span)
    while True:
        try:
            answer = input("Model year(s) of your %s (Enter to skip): " % model).strip().lower()
        except EOFError:
            print()
            return None
        if not answer:
            return None
        if answer == "all":
            wanted = [str(y) for y in range(first, last + 1)]
        elif re.match(r"^\d{4}(-\d{4})?(\s*,\s*\d{4}(-\d{4})?)*$", answer):
            wanted = tis_refsearch.years_of(answer.replace(" ", ""))
        else:
            print("    Please give years like 2024, 2022,2024, 2022-2024 or all")
            continue
        missing = [y for y in wanted if y not in years]
        wanted = sorted(y for y in wanted if y in years)
        if missing:
            print("    TIS has no %s %s.  It has: %s" % (model, ", ".join(missing), ", ".join(sorted(years))))
            if not wanted:
                continue
        return "%s:%s:%s" % (division, model.replace(" ", "_"), year_spec(wanted))


def year_spec(years):
    """2022,2023,2024,2026 -> 2022-2024,2026"""
    out, run = [], []
    for y in sorted(int(y) for y in years) + [None]:
        if run and (y is None or y != run[-1] + 1):
            out.append(str(run[0]) if len(run) == 1 else "%d-%d" % (run[0], run[-1]))
            run = []
        if y is not None:
            run.append(y)
    return ",".join(out)


def main():
    ap = argparse.ArgumentParser(description="Find a vehicle's manual codes from its make, model and year")
    ap.add_argument("vehicle", nargs="*", metavar="MAKE MODEL YEAR", help="ie: LEXUS LX600 2024 (anything left off is asked)")
    ap.add_argument("--args", action="store_true", help="print only the tis-clone arguments")
    ap.add_argument("--ref-for", metavar="TOC.XML", help="ask for the model year of the vehicle a downloaded manual is for "
                    "and print its --ref value (MAKE:MODEL:YEAR)")
    ap.add_argument("--wait", type=float, help="seconds between requests (default TIS_WAIT in tis-clone.cfg, or 0.01)")
    args = ap.parse_args()
    if len(args.vehicle) > 3:
        ap.error("give at most MAKE MODEL YEAR")

    # Everything but the answer goes to stderr (including tis-fetch's re-login messages)
    answer_to = sys.stdout
    sys.stdout = sys.stderr

    cfg = tis_refsearch.tis_fetch.load_cfg()
    os.makedirs(cfg["DOWNLOAD_TO"], exist_ok=True)
    rs = tis_refsearch.RefSearch(cfg, tis_refsearch.tis_fetch.wait_of(cfg, args.wait))
    if args.ref_for:
        try:
            ref = ask_ref(args.ref_for, rs)
        finally:
            rs.fetcher.save_cookies()
        if ref:
            print(ref, file=answer_to)
        return 0
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
    # The vehicle, for the Reference Information download (one word: tis-clone splits its saved arguments)
    tis_args.append("--ref %s:%s:%s" % (division, model.replace(" ", "_"), year))

    out = sys.stderr if args.args else answer_to
    print(file=out)
    for option, title, tab, prefixes in SECTIONS:
        names = [prefix + code for (prefix, code), n in found[option].most_common()]
        print("    %-24s %s%s" % (title, names[0] if names else "none",
                                  "  (also: %s)" % ", ".join(names[1:]) if len(names) > 1 else ""), file=out)
    print("\nTo download them:  %s/tis-clone %s" % (os.path.dirname(cfg["SCRIPT_BASE"]), " ".join(tis_args)), file=out)
    print("(--ref also downloads the owner's manuals and other Reference Information; see dl-ref.sh)", file=out)
    if args.args:
        print(" ".join(tis_args), file=answer_to)
    return 0


if __name__ == "__main__":
    sys.exit(main())
