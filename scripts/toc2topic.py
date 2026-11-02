#!/usr/bin/env python3
#
# toc2topic.py - Print the vehicle a manual is for, from its toc.xml or wiring diagram termdata.xml
#
# ie: "TOYOTA 2013-2018 RAV4 Repair Manual (RM30B0U)" prints "TOYOTA 2013-2018 RAV4".  tis-mkpdfs.sh uses it
# to name the PDF folder.
#
# Usage:
#   toc2topic.py toc.xml|termdata.xml
#   toc2topic.py --pick TOC ...      the vehicle of the one covering the fewest years (the first, of those):
#                                    tis-clone names a run's PDF folder with it, so the 1998 Land Cruiser's
#                                    is "Toyota 1998 Land Cruiser", not its A340 manual's "Toyota 1995-2002 ..."
#

import re
import sys
import xml.etree.ElementTree as ET


def topic_of(toc):
    try:
        root = ET.parse(toc).getroot()
    except (OSError, ET.ParseError) as e:
        sys.exit("%s: can't read %s: %s" % (sys.argv[0], toc, e))
    topic = root.findtext("name") or root.findtext("pubtitle") or ""
    topic = re.sub(r" (Body|Collision|Repair|New Car|Electrical|Flat Rate|\S+ (Automatic|Manual) Transmission).*$", "", topic)
    return re.sub(r" \([A-Za-z0-9]+\)$", "", topic)


def span(topic):
    """How many years a title covers (a title without a year last)"""
    years = [int(y) for y in re.findall(r"\b(?:19|20)\d\d\b", topic)]
    return max(years) - min(years) if years else 1000


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--pick":
        topics = [topic_of(t) for t in sys.argv[2:]]
        print(min(topics, key=span))
    elif len(sys.argv) == 2:
        print(topic_of(sys.argv[1]))
    else:
        sys.exit("Syntax: %s toc.xml | --pick toc.xml ..." % sys.argv[0])


if __name__ == "__main__":
    main()
