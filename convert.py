#!/usr/bin/env python

# convert.py
# move <chart>.sm to "<title> - <artist>"

import os
import sys

from simfile import SMParser


def main():
    try:
        simfile = sys.argv[1]
    except IndexError:
        print "usage: %s /path/to/simfile.sm" % sys.argv[0]
        sys.exit(1)

    base = os.path.dirname(os.path.abspath(simfile))

    parsed = SMParser(open(simfile).read())
    new_title = parsed.TITLE + " - " + parsed.ARTIST
    new_simfile = base + '/' + new_title

    print "moving %s to %s" % (simfile, new_simfile)
    os.rename(simfile, new_simfile)

if __name__ == "__main__":
    sys.exit(main())
