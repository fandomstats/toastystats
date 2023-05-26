import sys
import AO3search
from convert import convertToAO3
import time
from toastyTools import getListFromTextFile, getNumWorksFromURL, setupUrllib, getAO3SimpleTagURL, getAO3TagWordCountURL

if len(sys.argv) < 5:
    sys.exit('Usage: %s tagfile csvfile min_word_count max_word_count (e.g., getWordCountInfo tags.txt out.csv "50000" "")' % sys.argv[0])

verbose = True

tagfile = sys.argv[1]
csvfile = sys.argv[2]
minWC = sys.argv[3]
maxWC = sys.argv[4]

fo = open(csvfile, "w")

# get the list of tags
tags = getListFromTextFile(tagfile)

# write headers
fo.write("tag,num works,num works with "+minWC+"-"+maxWC+" words\n")


for t in tags:
    fo.write(t + ",")
    if verbose:
        print(t)
        
    includeTags = []
    excludeTags = []
    urls = []
    setupUrllib()


    # url for tag's works
    urls.append(getAO3SimpleTagURL(t))
    # url for tag limited to works with the desired word count
    urls.append(getAO3TagWordCountURL(t, minWC, maxWC))

    for u in urls:
        numWorks = getNumWorksFromURL(u, True)
        if verbose:
            print(numWorks)
        fo.write(str(numWorks) + ",")
    
    fo.write("\n")
    

fo.close()
