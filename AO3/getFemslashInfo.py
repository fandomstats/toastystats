import sys
import AO3search
from convert import convertToAO3
import time
from toastyTools import getListFromTextFile, getAO3TagURL, getAO3TagTimeframeURL, getNumWorksFromURL, setupUrllib, getAO3SimpleTagURL

if len(sys.argv) < 5:
    sys.exit('Usage: %s tagfile csvfile startdate enddate (e.g., getFemslashInfo tags.txt out.csv "2020-01-01" "2020-12-31")' % sys.argv[0])

verbose = True

tagfile = sys.argv[1]
csvfile = sys.argv[2]
startdate = sys.argv[3]
enddate = sys.argv[4]

fo = open(csvfile, "w")

# get the list of tags
tags = getListFromTextFile(tagfile)

# write headers
fo.write("tag,num works,F/F,F/F -M/M -F/M,F/F -M/M -F/M between "+startdate+" and "+enddate+"\n")


for t in tags:
    fo.write(t + ",")
    if verbose:
        print(t)
        
    includeTags = []
    excludeTags = []
    urls = []
    setupUrllib()


    # url for tag's num works
    urls.append(getAO3SimpleTagURL(t))
    # url for tag + F/F
    includeTags.append("F/F")
    urls.append(getAO3TagURL(t, includeTags, excludeTags))
    # url for tag + F/F -M/M -F/M
    excludeTags.append("F/M")
    excludeTags.append("M/M")
    urls.append(getAO3TagURL(t, includeTags, excludeTags))
    # url for tag + F/F -M/M -F/M in a given time frame
    urls.append(getAO3TagTimeframeURL(t, includeTags, excludeTags, startdate, enddate))

    for u in urls:
        # TO DO: would ideally like to get not just num works, but also top category and top fandom
        numWorks = getNumWorksFromURL(u, True)
        if verbose:
            print(numWorks)
        fo.write(str(numWorks) + ",")
    
    fo.write("\n")
    

fo.close()
