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
from toastyTools import getArguments, setupUrllib, getSearchURL, mergeDictionaries, writeDictToCSV

# GLOBAL VARIABLES
DEBUG = 0


############# BEGIN MAIN FUNCTION

numArgs = 7
args = getArguments(sys.argv, numArgs, 'Usage: topShipsAndFandoms [primary tag] [include tags file] [exclude tags file] [recursion depth] [ships outfile] [chars out] [fandoms out] (e.g.: topShipsAndFandoms "F/F" "include.tags" "exclude.tags" 5 "ships.csv" "characters.csv" "fandoms.csv")\n')

if DEBUG:
    print args

tag, includefile, excludefile, recursionDepth, shipOut, fandomOut, charOut = args[0:numArgs]
recursionDepth = int(recursionDepth)

includeTags = []
excludeTags = []

# these dictionaries have values that are the MINIMUM number of works
# that fit the given search criteria.  they are mostly underestimates,
# thanks to tag exclusions and meta tags not being accounted for in
# the Sort & Filter sidebar
topShips = {}
topFandoms = {}
topCharacters = {}

includeTags = [line.rstrip('\n') for line in open(includefile)]
excludeTags = [line.rstrip('\n') for line in open(excludefile)]
if DEBUG:
    print includeTags
    print excludeTags

http = setupUrllib()

for i in range(recursionDepth):
    url = getSearchURL(tag, includeTags, excludeTags)
    print i
    if DEBUG:
        print url

    # create an AO3 search object for the tag
    tagData = AO3search.AO3data()
    tagData.searchURL = url

    # get the top 10 ships and fandoms
    tagData.getTopInfo()
    fandoms = tagData.categories["fandom"]["top"]
    ships = tagData.categories["relationship"]["top"]
    chars = tagData.categories["character"]["top"]
    if DEBUG:
        print fandoms
        print ships
        print chars

    # merge the dictionaries into topFandoms and topShips
    topFandoms = mergeDictionaries(topFandoms, fandoms)
    topShips = mergeDictionaries(topShips, ships)
    topCharacters = mergeDictionaries(topCharacters, chars)

    # exclude the top ships (but not the fandoms, because there may be
    # other ships that match the search criteria in the same fandom)
    excludeTags = list(set().union(ships.keys(), excludeTags))

    if DEBUG:
        print topFandoms
        print topShips
        print topCharacters
        print excludeTags
    
writeDictToCSV(topShips, shipOut)
writeDictToCSV(topFandoms, fandomOut)
writeDictToCSV(topCharacters, charOut)
