import re
import sys
import time
import os

#MAXMONTHS = 50

if len(sys.argv) < 6:
    sys.exit('Usage: %s fandom freeform_tag time_period number_of_periods outfile' % sys.argv[0])

verbose = False

#if len(sys.argv) > 6:
#    arg = sys.argv[6]
#    if arg == "-verbose" or arg == "-v":
#        verbose = True

fandom = sys.argv[1]
freeform = sys.argv[2]
timep = sys.argv[3]
nump = int(sys.argv[4])
outfile = sys.argv[5]

# **************************************


fout = open(outfile, "w")
fout.write("{ \"searches\": [\n")

# iterate through all time slices except the last one
for t in range(1, nump):
    
    # write to outfile
    fout.write("{ \"fandom\": \"")
    fout.write(fandom)
    fout.write("\",")    
    fout.write(" \"freeform\": \"")
    fout.write(freeform)
    fout.write("\",")    
    fout.write(" \"date\": \"")
    fout.write(str(t))
    fout.write(" ")
    fout.write(str(timep))
    fout.write("s ago\"},\n")    

# treat the last item differently -- no final comma
fout.write("{ \"fandom\": \"")
fout.write(fandom)
fout.write("\",")    
fout.write(" \"freeform\": \"")
fout.write(freeform)
fout.write("\",")    
fout.write(" \"date\": \"")
fout.write(str(t+1))
fout.write(" ")
fout.write(str(timep))
fout.write("s ago\"}\n")    

fout.write("] }\n")


