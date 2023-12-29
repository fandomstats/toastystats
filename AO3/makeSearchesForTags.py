import re
import sys
import time
import os


if len(sys.argv) < 3:
    sys.exit('Usage: %s tagfile outfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 3:
    arg = sys.argv[3]
    if arg == "-verbose" or arg == "-v":
        verbose = True

tagfile = sys.argv[1]
outfile = sys.argv[2]

if verbose:
    print("tag file: ", tagfile)
    print("output  file: ", outfile)

try:
    with open(tagfile) as fin:
        tags = fin.readlines()
except:
    sys.exit("could not read input file")

if verbose:
    print("Number of lines: ", len(tags))

fout = open(outfile, "w")
fout.write("{ \"searches\": [\n")


# iterate through all items except the last one
for f in tags[:-1]:
    if verbose:
        print(f)
#    f = re.sub("\"", '%22', f)
    f = re.sub("\"", '\\\"', f)
    f = f.rstrip("\n")

    if verbose:
        print("tag: ", f)

    # write to outfile
    fout.write("{ \"tag\": \"")
    fout.write(f)
    fout.write("\"},\n")    

# treat the last item differently -- no final comma
f = tags[-1]
#f = re.sub("\"", '%22', f)
f = re.sub("\"", '\\\"', f)
f = f.rstrip("\n")
if verbose:
    print("tag: ", f)

fout.write("{ \"tag\": \"")
fout.write(f)
fout.write("\"}\n")    

fout.write("] }\n")


