import numpy as np
#import pandas as pd
#import xarray as xr
import sys
import io
import re
#import toastyTools

verbose = True

def writeTagToFile(tag, fp):
    fp.write(str(tag["id"]) + ",")
    fp.write(tag["type"] + ",")
    fp.write(tag["name"] + ",")
    fp.write(str(tag["canonical"]) + ",")
    fp.write(str(tag["cached_count"]) + ",")
    fp.write(str(tag["merger_id"]) + ",")
    fp.write("\n")


if len(sys.argv) < 3:
    sys.exit('Usage: %s csvfile outfileDirectory' % sys.argv[0])

csvfile = sys.argv[1]
outdir = sys.argv[2]

# load in the tag Data as an NDarray
with io.open(csvfile, 'r', encoding='UTF-8') as f:
    tagData = np.genfromtxt(f, dtype={'names': ('id', 'type', 'name', 'canonical', 'cached_count', 'merger_id'),
                                        'formats': ('i4', 'U100', 'U100', '?', 'i4', 'i4')}, skip_header=1, delimiter=',', comments=None)


outfiles = {}
header = "id, type, name, canonical, cached_count, merger_id"
polyfp = open(outdir + "/Polyships-canonical.csv", 'w')
polyfp.write(header + "\n")
bigshipfp = open(outdir + "/Bigships-canonical.csv", 'w')
bigshipfp.write(header + "\n")

# create a new outfile for each tag type (e.g., "Relationship", "Character")
for tag in tagData:
    if tag["canonical"]:
        ttype = tag["type"]
        if ttype in list(outfiles.keys()):
            fp = outfiles[ttype]
            writeTagToFile(tag, fp)
        else:
            outfileName = outdir + "/" + ttype + "-canonical.csv"
            fp = open(outfileName, 'w')
            outfiles[ttype] = fp
            fp.write(header + "\n")
            writeTagToFile(tag, fp)
            
        #Also write poly and bigger relationships to their own file
        if ttype == "Relationship":
            ship =  tag["name"]
            if  re.search("\/.+\/", ship):
                #print ship
                writeTagToFile(tag, polyfp)
            if tag["cached_count"] >= 10:
                writeTagToFile(tag, bigshipfp)
