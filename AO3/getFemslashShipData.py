from bs4 import BeautifulSoup
import urllib3
import certifi
import re
import sys
import string
import csv
import time
import codecs
import operator
import convert
import AO3search
from random import randint
from pprint import pprint


# GLOBAL VARIABLES
DEBUG = 1
PAUSE_BETWEEN_FETCHES = 2

# TAG OBJECT
class AO3Tag:
    name = ""
    tagStyle = None
    searchStyle = None
    def __init__(self, tagName):
        self.name = tagName
        ##### there's a bug right here for fandoms with non-ascii characters...
        tmp = convert.convertToAO3(tagName, "tag", False)
        self.tagStyle = tmp[0]
        tmp = convert.convertToAO3(tagName, "unsorted", False)
        self.searchStyle = tmp[0]

# CONSTRUCT APPROPRIATE URL FN
def makeURL(pageType, tag):
    if pageType == "shipWorks":
        return("https://archiveofourown.org/tags/" + tag.tagStyle + "/works")
    elif pageType == "shipNoFMMM":
        return("https://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D=&exclude_work_search%5Bcategory_ids%5D%5B%5D=22&exclude_work_search%5Bcategory_ids%5D%5B%5D=23&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&tag_id=" + tag.searchStyle)
    elif pageType == "shipPastYear":
        return("https://archiveofourown.org/works/search?utf8=%E2%9C%93&commit=Search&work_search%5Bquery%5D=&work_search%5Btitle%5D=&work_search%5Bcreators%5D=&work_search%5Brevised_at%5D=%3C+1+year&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bsingle_chapter%5D=0&work_search%5Bword_count%5D=&work_search%5Blanguage_id%5D=&work_search%5Bfandom_names%5D=&work_search%5Brating_ids%5D=&work_search%5Bcharacter_names%5D=&work_search%5Brelationship_names%5D=" + tag.searchStyle + "&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=_score&work_search%5Bsort_direction%5D=desc")
    elif pageType == "fandomWorks":
        return("https://archiveofourown.org/tags/" + tag.tagStyle + "/works")
    elif pageType == "fandomNoFMMM":
        return("https://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&include_work_search%5Bcategory_ids%5D%5B%5D=116&work_search%5Bother_tag_names%5D=&exclude_work_search%5Bcategory_ids%5D%5B%5D=22&exclude_work_search%5Bcategory_ids%5D%5B%5D=23&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&tag_id=" + tag.searchStyle)
    elif pageType == "fandomFFWorks":
        return("https://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&include_work_search%5Bcategory_ids%5D%5B%5D=116&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&tag_id="+ tag.tagStyle)
    elif pageType == "fandomPastYear":
        return("https://archiveofourown.org/works/search?utf8=%E2%9C%93&commit=Search&work_search%5Bquery%5D=&work_search%5Btitle%5D=&work_search%5Bcreators%5D=&work_search%5Brevised_at%5D=%3C+1+year&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bsingle_chapter%5D=0&work_search%5Bword_count%5D=&work_search%5Blanguage_id%5D=&work_search%5Bfandom_names%5D=" + tag.searchStyle + "&work_search%5Brating_ids%5D=&work_search%5Bcategory_ids%5D%5B%5D=116&work_search%5Bcharacter_names%5D=&work_search%5Brelationship_names%5D=&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=_score&work_search%5Bsort_direction%5D=desc")


def getNumWorksAsString(tag, searchType, isSortAndFilterPage):
    ao3Tag = AO3Tag(tag)
    tagData = AO3search.AO3data()
    tagData.searchURL = makeURL(searchType, ao3Tag)
    tagData.getNumWorks(isSortAndFilterPage)
    return str(tagData.numworks)


############# BEGIN MAIN FUNCTION


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
reload(sys)  
sys.setdefaultencoding('utf8')

# basic error checking for right number of arguments
if len(sys.argv) < 3:
    sys.exit('Usage: %s [infile containing ships, one per line] [outfile] (e.g.: %s "femslash_ships.txt" "ship_info.csv")\n' % (sys.argv[0],sys.argv[0]))

infile, outfile = sys.argv[1:3]

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

fandomNumbers = {}
shipList = []
#op = open(outfile, "w")
op = codecs.open(outfile, encoding='utf-8', mode="w+")
op.write("ship, ship works, ship -M/M -F/M, ship past year, fandom, fandom works, fandom -M/M -F/M, fandom F/F, fandom past year\n")

# read in the ship names
try:  
#    fp = codecs.open(infile, encoding='utf-8')
    fp = open(infile, "r")
    for s in fp:
        shipList.append(s.strip()) 
#    if (DEBUG):
#        print(shipList)
finally:  
    fp.close()

# for each ship...
for ship in shipList:
    
    if DEBUG:
        print ship

    shipTag = AO3Tag(ship)
    shipData = AO3search.AO3data()
    output = [ship]

    # fetch the main tag page
    shipData.searchURL = makeURL("shipWorks", shipTag)
    # find total ship works
    shipData.getNumWorks(True)
    output.append(str(shipData.numworks))

    # get the number of works for the ship -F/M -M/M
    output.append(getNumWorksAsString(ship, "shipNoFMMM",True))
    # get the number of works for the ship in the past year
    output.append(getNumWorksAsString(ship, "shipPastYear",False))

    # identify main fandom
    try:
        shipData.getTopInfo()
        fandoms = shipData.categories["fandom"]["top"]
        topFandom = max(fandoms.iteritems(), key=operator.itemgetter(1))[0]
    except:
        topFandom = "N/A"
        print "ERROR fetching top fandom"
    output.append(topFandom)

    # get the total number of works for the fandom, and fandom
    # breakdowns of interest
    if topFandom is not "N/A":

        fn = {}
        try:
            if topFandom not in fandomNumbers.keys():
                fn["fandomWorks"] = getNumWorksAsString(topFandom, "fandomWorks",True)
                fn["fandomNoFMMM"] = getNumWorksAsString(topFandom, "fandomNoFMMM",True)
                fn["fandomFFWorks"] = getNumWorksAsString(topFandom, "fandomFFWorks",True)
                fn["fandomPastYear"] = getNumWorksAsString(topFandom, "fandomPastYear",False)
                fandomNumbers[topFandom] = fn
            else:    
                fn = fandomNumbers[topFandom]
        except:
            print "ERROR fetching fandom detailed stats"

        try:
            fn = fandomNumbers[topFandom]
            output.append(fn["fandomWorks"])
            output.append(fn["fandomNoFMMM"])
            output.append(fn["fandomFFWorks"])
            output.append(fn["fandomPastYear"])
        except:
            output.append("-2")
            output.append("-2")
            output.append("-2")
            print "ERROR adding fandom numbers to output"

    else:
        output.append("-2")
        output.append("-2")
        output.append("-2")

    # print the data to the outfile
    if (DEBUG):
        print output
    separator = ", "
    op.write(separator.join(output) + "\n")
    
    # pause to avoid inadvertant DOS attack
#    time.sleep(PAUSE_BETWEEN_FETCHES)

op.close()
