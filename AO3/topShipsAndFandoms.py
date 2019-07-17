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
#import convert
import AO3search
from toastyTools import getArguments, setupUrllib, getAO3SearchURL, mergeDictionaries, writeDictToCSV, getAO3TagURL

# GLOBAL VARIABLES
DEBUG = 1
LOGIC_ONLY = 1

def removeBadShips(ships, include, exclude, existingShips):
    shipsToRemove = []
    ind = 1
    numShips = len(ships)
    for s in ships:
        if DEBUG:
            print "deep dive on ship " + s + "(" + str(ind) + "/" + str(numShips) + ")"
        ind+=1
        # don't both if we've already processed this ship
        if s not in existingShips and s not in exclude:
            # get the number of works for the ship overall
            shipData = AO3search.AO3data()
            allWorksURL = getAO3SearchURL(s, [], [])
            shipData.searchURL = allWorksURL
            shipData.getNumWorks(True)
            totalWorks = shipData.numworks
            if DEBUG:
                #                    print allWorksURL
                print totalWorks
                # get the number of works for the ship + include tags + exclude tags
            restrictedShipData = AO3search.AO3data()
            restrictedURL = getAO3SearchURL(s, include, exclude)
            restrictedShipData.searchURL = restrictedURL
            restrictedShipData.getNumWorks(True)
            restrictedWorks = restrictedShipData.numworks
            # now remove the ship from the list if the majority of
            # its works don't fit the include/exclude criteria
            if DEBUG:
#                    print restrictedURL 
                print restrictedWorks
                print restrictedWorks/float(totalWorks)
            if restrictedWorks/float(totalWorks) < 0.5:
                shipsToRemove.append(s)
                if DEBUG:
                    print "EXCLUDE THIS SHIP" 

    for r in shipsToRemove:
        print "removing ship " + r
        del ships[r]
    return ships

###### getTopShipsAndFandoms
# this is a function that can be called by other functions and returns
# a data object.  There's also a wrapper function at the end of the
# file that lets one call this from the command line and print results
# to CSV
def getTopShipsAndFandoms(tag, includeTags, excludeTags, recursionDepth, minShipSize):

    originalExcludeTags = excludeTags[:] #because we'll be adding more
    completeIncludeTags = includeTags
    completeIncludeTags.append(tag)

# these dictionaries have values that are the MINIMUM number of works
# that fit the given search criteria.  they are mostly underestimates,
# thanks to tag exclusions and meta tags not being accounted for in
# the Sort & Filter sidebar
    topData = {}
    topData["ships"] = {}
    topData["fandoms"] = {}


    http = setupUrllib()

    for i in range(recursionDepth):
        fandoms = []
        ships = []
        iter = str(i+1)
        url = getAO3SearchURL(tag, includeTags, excludeTags)
        print iter
#        if DEBUG:
#            print url

        # create an AO3 search object for the tag
        tagData = AO3search.AO3data()
        tagData.searchURL = url

        # get the top 10 ships and fandoms
        tagData.getTopInfo()
        fandoms = tagData.categories["fandom"]["top"]
        ships = tagData.categories["relationship"]["top"]
        if DEBUG:
            print iter + ". fandoms" 
            print fandoms
            print iter + ". ships" 
            print ships

        # exclude the top ships and fandoms
        excludeTags = list(set().union(ships.keys(), fandoms.keys(), excludeTags))

        ships = removeBadShips(ships, completeIncludeTags, originalExcludeTags, topData["ships"].keys())
                
        # merge the dictionaries into topFandoms and topShips
        topData["fandoms"] = mergeDictionaries(topData["fandoms"], fandoms)
        topData["ships"] = mergeDictionaries(topData["ships"], ships)

        if DEBUG:
            print topData
            print excludeTags
    

    # for each of the top fandoms, also check for more ships that
    # fit the criteria
    ind = 1
    numFandoms = len(topData["fandoms"].keys())
    for f in topData["fandoms"].keys():
        if DEBUG:
            print iter + ". deep dive on fandom " + f + " (" + str(ind) + "/" + str(numFandoms) + ")"
            ind+=1
        # don't both if we've already processed this fandom
#        if f not in topData["fandoms"].keys():
        smallestShipSize = minShipSize + 1
        tmpExcludeTags = originalExcludeTags[:]
        # keep excluding top 10 ships and fetching more until
        # the minimum size is reached (keeping in mind that
        # the numbers will be off due to exclusions)
        while smallestShipSize > minShipSize:
            topFandomShips = {}
            fandomData = AO3search.AO3data()
            url = getAO3SearchURL(f, completeIncludeTags, tmpExcludeTags)
            fandomData.searchURL = url
            fandomData.getTopInfo()
            topFandomShips = fandomData.categories["relationship"]["top"]
            tmpExcludeTags += topFandomShips.keys()
            topFandomShips = removeBadShips(topFandomShips, completeIncludeTags, originalExcludeTags, topData["ships"].keys())
            ships = mergeDictionaries(ships, topFandomShips)
            #                    if DEBUG:
            #                        print ships
            smallestShip = min(topFandomShips, key=topFandomShips.get)
            smallestShipSize = topFandomShips[smallestShip]
            if DEBUG:
                print "smallestShip: " + smallestShip + " (" + str(smallestShipSize) + ")"
                    #                        print smallestShip
                    #                        print smallestShipSize
                                          
        # for each of the ships, check that the majority of the ship's
        # works do NOT use the exclude tags

    return topData

############# BEGIN MAIN FUNCTION


args = getArguments(sys.argv, 7, 'Usage: topShipsAndFandoms [primary tag] [include tags file] [exclude tags file] [recursion depth] [min ship size] [outfile] (e.g.: topShipsAndFandoms "F/F" "include.tags" "exclude.tags" 5 100 "ships.csv" "fandoms.csv")\n')

if DEBUG:
    print args

tag, includefile, excludefile, recursionDepth, minShipSize, shipOut, fandomOut = args[0:7]
recursionDepth = int(recursionDepth)
minShipSize = int(minShipSize)

includeTags = [line.rstrip('\n') for line in open(includefile)]
excludeTags = [line.rstrip('\n') for line in open(excludefile)]
if DEBUG:
    print includeTags
    print excludeTags

topData = getTopShipsAndFandoms(tag, includeTags, excludeTags, recursionDepth, minShipSize)

writeDictToCSV(topData["ships"], shipOut)
writeDictToCSV(topData["fandoms"], fandomOut)
