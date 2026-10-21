#!/usr/bin/env python3
#
# toc2topic.py - Print the vehicle a manual is for, from its toc.xml or wiring diagram termdata.xml
#
# ie: "TOYOTA 2013-2018 RAV4 Repair Manual (RM30B0U)" prints "TOYOTA 2013-2018 RAV4".  tis-mkpdfs.sh uses it
# to name the PDF folder.
#
# Usage:
#   toc2topic.py toc.xml|termdata.xml
#

import re
import sys
import xml.etree.ElementTree as ET


def main():
    if len(sys.argv) != 2:
        sys.exit("Syntax: %s toc.xml" % sys.argv[0])
    try:
        root = ET.parse(sys.argv[1]).getroot()
    except (OSError, ET.ParseError) as e:
        sys.exit("%s: can't read %s: %s" % (sys.argv[0], sys.argv[1], e))
    topic = root.findtext("name") or root.findtext("pubtitle") or ""
    print(re.sub(r" (Body|Collision|Repair|New Car|Electrical|Flat Rate).*$", "", topic))


if __name__ == "__main__":
    main()
