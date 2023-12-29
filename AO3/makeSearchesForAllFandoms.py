import re
import sys
import time
import os


if len(sys.argv) < 3:
    sys.exit('Usage: %s fandomfile outfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 3:
    arg = sys.argv[3]
    if arg == "-verbose" or arg == "-v":
        verbose = True

fandomfile = sys.argv[1]
outfile = sys.argv[2]

if verbose:
    print("fandom file: ", fandomfile)
    print("output  file: ", outfile)

try:
    with open(fandomfile) as fin:
        fandoms = fin.readlines()
except:
    sys.exit("could not read fandom file")

if verbose:
    print("Number of lines: ", len(fandoms))

fout = open(outfile, "w")
fout.write("{ \"searches\": [\n")


# iterate through all items except the last one
for f in fandoms[:-1]:
    f = re.sub("\"", '%22', f)
    f = f.rstrip("\n")

    if verbose:
        print("fandom: ", f)

    # write to outfile
    fout.write("{ \"tag\": \"")
    fout.write(f)
    fout.write("\"},\n")    

# treat the last item differently -- no final comma
f = fandoms[-1]
f = re.sub("\"", '%22', f)
f = f.rstrip("\n")
if verbose:
    print("fandom: ", f)

fout.write("{ \"tag\": \"")
fout.write(f)
fout.write("\"}\n")    

fout.write("] }\n")


