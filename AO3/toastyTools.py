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
from convert import convertToAO3
import AO3search

#####
def getArguments(args, numArgs, errorMsg):
    if len(args) < numArgs+1:
        sys.exit(errorMsg)
    else:
        return args[1:numArgs+1]

#####
def setupUrllib():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    reload(sys)
    sys.setdefaultencoding('utf8')
    return urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


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
def getAO3TagURL(tag):
    formattedTag = convertToAO3(tag, "tag", False)
    return("https://archiveofourown.org/tags/" + formattedTag[0] + "/works")

def getAO3TagStructureURL(tag):
    formattedTag = convertToAO3(tag, "tag", False)
    return("https://archiveofourown.org/tags/" + formattedTag[0] + "/")

##### getSearchURL
# creates a search URL for a given combination of tags and tag
# exclusions.  the "main" tag is first argument, but any of the
# include tags can also be the main tag (duplication okay).  either
# include or exclude can also be empty.

def getAO3SearchURL(tag, includeTags, excludeTags):
    url = "https://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D="
    url = addListOfTags(url, includeTags)
    url += "&work_search%5Bexcluded_tag_names%5D="
    url = addListOfTags(url, excludeTags)
    ao3tag = convertToAO3(tag, "tag", False)
    url = url + "&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&tag_id=" + ao3tag[0]
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
    return max(mydict.items(), key=operator.itemgetter(1))[0]

def getSmallestKeyByValue(mydict):
    return min(mydict.items(), key=operator.itemgetter(1))[0]

####
def writeDictToCSV(mydict, filename):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in sorted(mydict.items(), key=operator.itemgetter(1), reverse=True):
#            key=key.encode('utf-8')
            writer.writerow([key, value])
