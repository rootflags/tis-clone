#!/usr/bin/env python3
#
# pdfjoin.py - Join PDFs into one, in the order given, with a bookmark for each
#
# tis-mkpdfs.sh joins TIS's one-PDF-per-diagram wiring diagrams with it.  Ghostscript did that before, but
# Ubuntu's AppArmor profile for gs only lets it use files under your home folder, /tmp, /mnt and /media, so it
# failed for downloads anywhere else (ie: /data/www).  Each bookmark is the file's name without .pdf.  A file
# that can't be read is skipped with a warning.  The output is written as OUT.part and renamed when done.
#
# Usage:
#   pdfjoin.py OUT.pdf IN.pdf ...
#
# Exit status: 0 done, 1 nothing could be joined (no OUT is written) or bad arguments.
#
# Requirements: python3-pikepdf
#

import os
import sys

import pikepdf


def main():
    if len(sys.argv) < 3:
        sys.exit("Syntax: %s OUT.pdf IN.pdf ..." % sys.argv[0])
    out, ins = sys.argv[1], sys.argv[2:]
    joined = pikepdf.Pdf.new()
    sources = []        # pikepdf needs them open until the joined PDF is saved
    marks = []
    for name in ins:
        try:
            src = pikepdf.open(name)
        except (pikepdf.PdfError, OSError) as e:
            print("    skipping %s: %s" % (name, e), file=sys.stderr)
            continue
        sources.append(src)
        marks.append((os.path.splitext(os.path.basename(name))[0], len(joined.pages)))
        joined.pages.extend(src.pages)
    if not sources:
        print("    nothing to join for %s" % out, file=sys.stderr)
        return 1
    with joined.open_outline() as outline:
        for title, page in marks:
            outline.root.append(pikepdf.OutlineItem(title, page))
    joined.save(out + ".part", compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    os.replace(out + ".part", out)
    for src in sources:
        src.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
