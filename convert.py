#!/usr/bin/env python

# convert.py
# move <chart>.sm to "<title> - <artist>"

import os
import regex as re
import sys

from simfile import SMParser

pattern = re.compile(r'([\p{IsHan}\p{IsBopo}\p{IsHira}\p{IsKatakana}]+)', re.UNICODE)

def main():
    try:
        simfile = sys.argv[1]
    except IndexError:
        print "usage: %s /path/to/simfile.sm" % sys.argv[0]
        sys.exit(1)

    base = os.path.dirname(os.path.abspath(simfile))
    parsed = SMParser(open(simfile).read())
    title = parsed.TITLE.decode('utf-8')

    if pattern.match(title):
        try:
            romanized_title = parsed.TITLETRANSLIT
        except:
            romanized_title = ""

        # Fall back to the file name if TITLETRANSLIT is empty
        if romanized_title == "":
            romanized_title = os.path.basename(simfile)[:-3]

        new_title = (parsed.TITLE +
                     " (" + romanized_title.strip('.') + ") " +
                     " - " +
                     parsed.ARTIST).replace('/', '')
    else:
        new_title = (parsed.TITLE + " - " + parsed.ARTIST).replace('/', '')

    new_simfile = base + '/' + new_title

    print "moving %s to %s" % (simfile, new_simfile)
    os.rename(simfile, new_simfile)

if __name__ == "__main__":
    sys.exit(main())
