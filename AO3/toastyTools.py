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
import io
from convert import convertToAO3#, convertFromAO3
import importlib
#import AO3search

PAUSE_INTERVAL = 10

#####
def getArguments(args, numArgs, errorMsg):
    if len(args) < numArgs+1:
        sys.exit(errorMsg)
    else:
        return args[1:numArgs+1]

#####
# Take in a file with a separate tag/fandom/language/etc on each line,
# in UTF encoding, and return it as a list
def getListFromTextFile(filename):
    fp = io.open(filename, "r")
    lines = fp.read().splitlines() 
#    lines = fp.readlines()
    return lines

#####
# Setup and return a file pointer to an outfile that writes UTF
# strings; also write the header row to the CSV
def prepCSVOutfile(filename, headers):
    outfp = io.open(filename, "w")
    outfp.write(headers)
    outfp.write("\n")
    return outfp

#####
# Write to CSV with correct encoding handling and add comma. strips whitespace.
def writeFieldToCSV(outfp, text):
    # added this to try to fix some special characters weirdness Feb 2021
    # at best this is a patch on issues somewhere else with string formatting though :-/
#    text = convertFromAO3(text, False)
    outfp.write(text)
    outfp.write(",")

def writeEndlineToCSV(outfp):
    outfp.write("\n")

#####
def setupUrllib():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    importlib.reload(sys)
    user_agent = {'user-agent': 'bot'}
    return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(), headers=user_agent)

#####
def getSoupFromURL(url):
    http = setupUrllib()
    r = {}
    try:
        print("Pausing so as not to DOS AO3...")
        time.sleep(PAUSE_INTERVAL) 
        r = http.request('GET', url)
        soup = BeautifulSoup(r.data, features="html.parser")
        soup.prettify()
        return soup
    except: #urllib.error.HTTPError as e:
        print("failure to fetch URL: ", url)
        return -1


#####
def addListOfTags(url, tagList):
    processedTags = []
    for tag in tagList:
        ao3tag = convertToAO3(tag, "unsorted", False)
        url += ao3tag[0]
        processedTags.append(tag)
        if len(processedTags) < len(tagList):
            url += "%2C"
    return url

#####
def getAO3SimpleTagURL(tag):
    formattedTag = convertToAO3(tag, "tag", False)
    return("https://archiveofourown.org/tags/" + formattedTag[0] + "/works")

def getAO3TagStructureURL(tag):
    formattedTag = convertToAO3(tag, "tag", False)
    return("https://archiveofourown.org/tags/" + formattedTag[0] + "/")

####
def getAO3TagWordCountURL(tag, minWC, maxWC):
    formattedTag = convertToAO3(tag, "tag", False)
    url = "https://archiveofourown.org/works?work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D="+minWC+"&work_search%5Bwords_to%5D="+maxWC+"&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&commit=Sort+and+Filter&tag_id=" + formattedTag[0]
    return url

##### getAO3TagURL and getAO3TagTimeframeURL
# creates a search URL for a given combination of tags and tag
# exclusions.  the "main" tag is first argument, but any of the
# include tags can also be the main tag (duplication okay).  either
# include or exclude can also be empty.  The "timeframe" function
# includes a start date and end date as well (either can be empty).
# dates must be strings in format YYYY-MM-DD.

def getAO3TagTimeframeURL(tag, includeTags, excludeTags, startDate, endDate):
    url = "https://archiveofourown.org/works?work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D="
    url = addListOfTags(url, includeTags)
    url += "&work_search%5Bexcluded_tag_names%5D="
    url = addListOfTags(url, excludeTags)
    ao3tag = convertToAO3(tag, "tag", False)
    url = url + "&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D="
    url = url + startDate
    url = url + "&work_search%5Bdate_to%5D="
    url = url + endDate
    url = url + "&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&commit=Sort+and+Filter&tag_id=" + ao3tag[0]
    return url
    
######
# this is a special case of the above function in which start and end date are empty
def getAO3TagURL(tag, includeTags, excludeTags):
    url = getAO3SearchTimeframeURL (tag, includeTags, excludeTags, "", "")
    return url

######
# this is just a wrapper because this was the old (confusing) name of the function
def getAO3SearchURL(tag, includeTags, excludeTags):
    return getAO3TagURL(tag, includeTags, excludeTags)
def getAO3SearchTimeframeURL(tag, includeTags, excludeTags,startDate,endDate):
    return getAO3TagTimeframeURL(tag, includeTags, excludeTags,startDate,endDate)

##### getAO3LanguageTimeframeURL
# Specify a language code, a timeframe string like AO3 takes in Works
# Search (e.g., "< 200 days"), and a True/False parameter specifying
# whether to limit to single work chapters. Returns an unstructured
# Search format (no sort and filter)

def getAO3LanguageTimeframeURL(langCode, timeframeString, singleChapterOnly): #update this to remove the utf8
    url = "https://archiveofourown.org/works/search?utf8=%E2%9C%93&commit=Search&work_search%5Bquery%5D=&work_search%5Btitle%5D=&work_search%5Bcreators%5D=&work_search%5Brevised_at%5D="
    timeframeString, tmp = convertToAO3(timeframeString, "unsorted", False) 
    url += timeframeString
    url += "&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bsingle_chapter%5D="
    if singleChapterOnly:
        url += "1"
    url += "&work_search%5Bword_count%5D=&work_search%5Blanguage_id%5D="
    url += langCode
    url += "&work_search%5Bfandom_names%5D=&work_search%5Brating_ids%5D=&work_search%5Bcharacter_names%5D=&work_search%5Brelationship_names%5D=&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=_score&work_search%5Bsort_direction%5D=desc"
    return url


##### mergeDictionaries
# this merges two dictionaries, with primaryDict taking precedence in case of repeat keys
def mergeDictionaries(primaryDict, secondaryDict):
    tmp = {}
    tmp.update(secondaryDict)
    tmp.update(primaryDict)
    return tmp

def unionOfLists(list1, list2):
    return list(set().union(list1,list2))

def getBiggestKeyByValue(mydict):
    return max(list(mydict.items()), key=operator.itemgetter(1))[0]

def getSmallestKeyByValue(mydict):
    return min(list(mydict.items()), key=operator.itemgetter(1))[0]

####
def writeDictToCSV(mydict, filename):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in sorted(list(mydict.items()), key=operator.itemgetter(1), reverse=True):
#            key=key.encode('utf-8')
            writer.writerow([key, value])

##### getNumWorksFromURL and getNumWorksFromSoup
# wrappers for confusing AO3Search process.  takes in an AO3 url or BeautifulSoup obj and
# a bool specifying whether or not it's a Sort and Filter url.
            
def getNumWorksFromSoup(soup, isSortAndFilterURL):

#    print "************ getNumWorksFromSoup"

    isSorted = isSortAndFilterURL
    errorNum = -2
    numWorks = errorNum
    try:
#        print "************ try1"

        if isSorted:
            tag = soup.find_all(text=re.compile("[0-9,]+ Work(s)*( found)* in "))
        else:
            tag = soup.find_all(text=re.compile("[0-9,]+ Found"))
    except AttributeError:
#        print "************ except1"
        return errorNum

    try:
#        print "************ try2"
        line =  tag[0]
    except:
#        print "************ except2"
        line = ''
        print("No num works found")
        return errorNum

#    print "************ nums"
    nums = re.findall('[0-9,]+', line) # 
    if len(nums) == 0:
        return errorNum
    elif len(nums) == 1:
        numWorks = (nums[0])
    else:
        numWorks = (nums[2])

    return numWorks

    
def getNumWorksFromURL(url, isSortAndFilterURL):
    
    soup = getSoupFromURL(url)
    return getNumWorksFromSoup(soup, isSortAndFilterURL)
