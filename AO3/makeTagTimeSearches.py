import re
import sys
import time
import os

MAXMONTHS = 50

if len(sys.argv) < 4:
    sys.exit('Usage: %s fandom freeform outfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 4:
    arg = sys.argv[4]
    if arg == "-verbose" or arg == "-v":
        verbose = True

fandom = sys.argv[1]
freeform = sys.argv[2]
outfile = sys.argv[3]

# **************************************


fout = open(outfile, "w")
fout.write("{ \"searches\": [\n")

# iterate through all time slices except the last one
for t in range(1, MAXMONTHS-1):
    
    # write to outfile
    fout.write("{ \"fandom\": \"")
    fout.write(fandom)
    fout.write("\",")    
    fout.write(" \"freeform\": \"")
    fout.write(freeform)
    fout.write("\",")    
    fout.write(" \"date\": \"")
    fout.write(str(t))
    fout.write(" months ago\"},\n")    

# treat the last item differently -- no final comma
fout.write("{ \"fandom\": \"")
fout.write(fandom)
fout.write("\",")    
fout.write(" \"freeform\": \"")
fout.write(freeform)
fout.write("\",")    
fout.write(" \"date\": \"")
fout.write(str(MAXMONTHS))
fout.write(" months ago\"}\n")    

fout.write("] }\n")


