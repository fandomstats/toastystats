import numpy as np
#import pandas as pd
#import xarray as xr
import sys
import io
import re
#import toastyTools

verbose = True

def writeTagToFile(tag, tagLength, fp):
    fp.write(str(tag["id"]) + ",")
    fp.write(tag["type"] + ",")
    fp.write(tag["name"] + ",")
    fp.write(str(tag["canonical"]) + ",")
    fp.write(str(tag["cached_count"]) + ",")
    fp.write(str(tag["merger_id"]) + ",")
    fp.write(str(tagLength) + ",")
    fp.write("\n")


if len(sys.argv) < 4:
    sys.exit('Usage: %s infile outfile min_tag_length' % sys.argv[0])

infile = sys.argv[1]
outfile = sys.argv[2]
minLength = int(sys.argv[3])

# load in the tag Data as an NDarray
with io.open(infile, 'r', encoding='UTF-8') as f:
    tagData = np.genfromtxt(f, dtype={'names': ('id', 'type', 'name', 'canonical', 'cached_count', 'merger_id'),
                                        'formats': ('i4', 'U100', 'U100', '?', 'i4', 'i4')}, skip_header=1, delimiter=',', comments=None)


header = "id, type, name, canonical, cached_count, merger_id"
outfp = open(outfile, 'w')
outfp.write(header + "\n")

# write just the long tags to outfile (both canonical and non-)
for tag in tagData:
    tagName = tag["name"]
    tagLength = len(tagName)
    if tagLength > minLength:
        print(tagName)
        print(tagLength)
        writeTagToFile(tag, tagLength, outfp)
