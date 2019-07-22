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
from toastyTools import getArguments, setupUrllib, getAO3SearchURL, mergeDictionaries, writeDictToCSV, getAO3TagURL, getBiggestKeyByValue

# GLOBAL VARIABLES
DEBUG = 1
LOGIC_ONLY = 1
MAX_DEPTH = 1000

class Tag:
    name = ""
    topFandomOverall = "" #the most commonly used AO3 fandom tag for this tag
    totalWorks = -1 #the overall number of works for this tag
    topFandomQualifying = "" #the most commonly used AO3 fandom tag once the include/exclude requirements are met
    qualifyingWorks = -1 #the number of works in this tag that meet all the include/exclude requirements
    ratio = -1 #the ratio of works that qualify


###### AddNewTagToDict
# adds the tag to the dictionary. returns pointer to tag object.
def AddNewTagToDict(tagName, tagDict):
#    if tagName is not in tagDict.keys:
    tagData = Tag()
    tagData.name = tagName

    print "~~~~~~Adding a new tag: " + tagName

    tagDict[tagName] = tagData
    return tagDict[tagName]

def FetchTopTagInfo(primaryTag, includeTags, excludeTags):
    url = getAO3SearchURL(primaryTag, includeTags, excludeTags)
    primaryTagData = AO3search.AO3data()
    primaryTagData.searchURL = url
    primaryTagData.getTopInfo()
    primaryTagData.getNumWorks(True)
    return primaryTagData

###### FetchTop10ShipsAndFandoms
# fetches the top ships and fandoms in the Sort & Filter sidebar for a given tag
def FetchTop10ShipsAndFandoms(primaryTag, includeTags, excludeTags):
    primaryTagData = FetchTopTagInfo(primaryTag, includeTags, excludeTags)
    return(primaryTagData.categories["relationship"]["top"], primaryTagData.categories["fandom"]["top"])


def AddNumWorksAndTopFandom(tag, include, exclude):
    tagDataWithoutRestrictions = FetchTopTagInfo(tag.name, [], [])
    tag.totalWorks = tagDataWithoutRestrictions.numworks
    unrestrictedFandoms = tagDataWithoutRestrictions.categories["fandom"]["top"]
    tag.topFandomOverall = getBiggestKeyByValue(unrestrictedFandoms)
    qualifyingTagData = FetchTopTagInfo(tag.name, include, exclude)
    tag.qualifyingWorks = qualifyingTagData.numworks
    qualifyingFandoms = qualifyingTagData.categories["fandom"]["top"]
    tag.topFandomQualifying = getBiggestKeyByValue(qualifyingFandoms)
    tag.ratio = float(tag.qualifyingWorks)/float(tag.totalWorks)
    if DEBUG:
        print "Qualifying works: " + str(tag.qualifyingWorks) + "/" + str(tag.totalWorks) + " (" + str(round(100*tag.ratio)) + "%)"
    return tag

###### AddShip
# checks if a ship already exists in dictionary.  if not, adds a new Ship object and fetches data from AO3.
# Returns number of qualifying works (factoring in include/exclude restrictions)
def AddShip(shipName, include, exclude, pastShips):
#    print "~~~~~~adding Ship: " + shipName
    if shipName not in pastShips.keys():
        ship = AddNewTagToDict(shipName, pastShips)
        ship = AddNumWorksAndTopFandom(ship, include, exclude)
    else:
        if DEBUG:
            print "~~~~~~ship previously found: " + shipName
    return pastShips[shipName]

###### AddFandom
# checks if a fandom already exists in dictionary.  if not, adds a new Fandom object and fetches data from AO3.
# also adds all ships that aren't already in the ship dictionary.
# Returns number of qualifying works (factoring in include/exclude restrictions)
def AddFandom(fandomName, include, exclude, pastFandoms, pastShips, minShipSize):
    print ".......................................Fandom deep dive: " + fandomName
    if fandomName not in pastFandoms.keys():
        # get the basic fandom stats
        fandom = AddNewTagToDict(fandomName, pastFandoms)
        fandom = AddNumWorksAndTopFandom(fandom, include, exclude)

        # now get the info for all the ships -- unless the fandom is too small
        if fandom.qualifyingWorks < minShipSize:
            belowSizeThreshold = True
        else:
            belowSizeThreshold = False

        searchDepth = 1
        while not belowSizeThreshold:
#            print "FANDOM: " + fandomName + " recursion depth: " + str(recursionDepth)
            topS, topF = FetchTop10ShipsAndFandoms(fandomName, include, exclude)
            i = 1
            for shipName in topS:
                print "FANDOM DEEP DIVE: " + fandomName + "; depth " + str(searchDepth) + "; ship " + str(i) + "/" + str(len(topS))
                ship = AddShip(shipName, include, exclude, pastShips)
                if ship.qualifyingWorks < minShipSize:
                    print "~~~ship below size threshold"
                    belowSizeThreshold = True
                i += 1
            exclude = exclude + list(topS.keys())
            searchDepth += 1
    else:
        print "~~~~~~fandom previously found!"
    return pastFandoms[fandomName]

# note: this OVERWRITES the file
def writeShipsToFile(ships, filename):
    with open(filename, 'w') as csv_ships:
        swriter = csv.writer(csv_ships)
        swriter.writerow(["Ship", "Num works meeting requirements", "Top fandom meeting requirements", "Total works", "Top fandom overall", "Ratio of works meeting requirements"])
        for key in sorted(ships, key = lambda name: ships[name].qualifyingWorks, reverse=True):
            s = ships[key]
            if s.qualifyingWorks >= minShipSize:
                swriter.writerow([s.name, s.qualifyingWorks, s.topFandomQualifying, s.totalWorks, s.topFandomOverall, s.ratio])

# note: this OVERWRITES the file
def writeFandomsToFile(fandoms, filename):
    with open(filename, 'w') as csv_fandoms:
        fwriter = csv.writer(csv_fandoms)
        fwriter.writerow(["Fandom", "Num works meeting requirements", "Total works", "Ratio of works meeting requirements"])
        for key in sorted(fandoms, key = lambda name: fandoms[name].qualifyingWorks, reverse=True):
            f = fandoms[key]
            fwriter.writerow([f.name, f.qualifyingWorks, f.totalWorks, f.ratio])



###### PRIMARY FUNCTION: getTopShipsAndFandoms
# this is a function that can be called by other functions and returns
# a data object.  There's also a wrapper function at the end of the
# file that lets one call this from the command line and print results
# to CSV
def getTopShipsAndFandoms(primaryTag, includeTags, excludeTags, minShipSize, shipOut, fandomOut):

    originalExcludeTags = excludeTags[:] #because we'll be adding more
    completeIncludeTags = includeTags
    completeIncludeTags.append(primaryTag)

    # these dictionaries are not guaranteed to be complete for the smaller ships --
    # they are tracking every ship ever investigated by the algorithm, some of which
    # are smaller than the min threshold
    topShips = {}
    topFandoms = {}
    smallestShip = sys.maxsize

    http = setupUrllib()

    #MAX_DEPTH is a global variable set at beginning of this file.
    #This gives you the optional ability to govern how many times to
    #exclude previous ships & fandoms and repeat search
    for i in range(MAX_DEPTH):
        if smallestShip > minShipSize:
            fandoms = []
            ships = []
            iter = str(i+1)
            if DEBUG:
                print "*********** NEW BIG LOOP ITERATION: " + iter

            # fetch the tag page for the primary tag (e.g., "F/F")
            ships, fandoms = FetchTop10ShipsAndFandoms(primaryTag, includeTags, excludeTags)
            if DEBUG:
                print iter + ". fandoms"
                print fandoms
                print iter + ". ships"
                print ships

            #fetch data about each ship
            s = 1
            numShipsAboveThreshold = 0
            for shipName in ships:
                if DEBUG:
                    print "BIG LOOP ITERATION " + iter + "; SHIP " + str(s)
                ship = AddShip(shipName, includeTags, excludeTags, topShips)
                if ship.qualifyingWorks >= minShipSize:
                    numShipsAboveThreshold += 1
                else:
                    if ship.qualifyingWorks < smallestShip:
                        smallestShip = ship.qualifyingWorks
                s += 1

            if DEBUG:
                print "*** Number of ships above size threshold: " + str(numShipsAboveThreshold)
            if numShipsAboveThreshold > 0:
                #fetch data about each fandom and all its top ships
                f = 1
                for fandomName in fandoms:
                    if DEBUG:
                        print "BIG LOOP ITERATION " + iter + "; FANDOM " + str(f)
                    fandom = AddFandom(fandomName, includeTags, excludeTags, topFandoms, topShips, minShipSize)
                    f += 1

                # exclude these ships and fandoms next time through the BIG LOOP
                excludeTags = list(set().union(excludeTags,ships.keys(),fandoms.keys()))
                writeShipsToFile(topShips, shipOut)
                writeFandomsToFile(topFandoms, fandomOut)
            else:
                print "********** no ships surpassed size threshold!  Ending main fn."
                break

    return(topShips, topFandoms)

############# BEGIN WRAPPER FUNCTION

args = getArguments(sys.argv, 6, 'Usage: topShipsAndFandoms [primary tag] [include tags file] [exclude tags file] [min ship size] [ship outfile] [fandom outfile] (e.g.: topShipsAndFandoms "F/F" "include.tags" "exclude.tags" 100 "ships.csv" "fandoms.csv")\n')

tag, includefile, excludefile, minShipSize, shipOut, fandomOut = args[0:7]
minShipSize = int(minShipSize)

includeTags = [line.rstrip('\n') for line in open(includefile)]
excludeTags = [line.rstrip('\n') for line in open(excludefile)]

ships, fandoms = getTopShipsAndFandoms(tag, includeTags, excludeTags, minShipSize, shipOut, fandomOut)
