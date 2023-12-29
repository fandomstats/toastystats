import re
import sys
import os
import pdb


if len(sys.argv) < 3:
    sys.exit('Usage: %s fandomfile csvfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 3:
    arg = sys.argv[3]
    if arg == "-verbose" or arg == "-v":
        verbose = True

fanf = sys.argv[1]
outputf = sys.argv[2]

ao3data = open(outputf).read()
for fandom in open(fanf):
    fandom = fandom.rstrip()
#    pattern = re.compile("^" + fandom)
    pattern = "\n" + fandom
    if pattern in ao3data:
#    if re.search(pattern, ao3data) is not None:
        if (verbose):
            print("FOUND: ", fandom)
    else:
#        print "MISSING: ", fandom
#        pdb.set_trace()
        print(fandom)

