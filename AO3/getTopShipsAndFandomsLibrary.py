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
from toastyTools import setupUrllib, getAO3SearchURL, getAO3TagStructureURL, mergeDictionaries, writeDictToCSV, getAO3TagURL, getBiggestKeyByValue

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

    print("~~~~~~Adding a new tag: " + tagName)

    tagDict[tagName] = tagData
    return tagDict[tagName]

def FetchTopTagInfo(primaryTag, includeTags, excludeTags):
    print("fetching top tag info: " + primaryTag) 
    print("excluding: ")
    print(excludeTags) 
#    time.sleep(PAUSE_INTERVAL)
    url = getAO3SearchURL(primaryTag, includeTags, excludeTags)
#    if DEBUG:
#       print "including " +  str(len(includeTags)) + " tags: "
#       print includeTags
#       print "excluding " + str(len(excludeTags)) + " tags: "
#       print excludeTags
#        print url
    primaryTagData = AO3search.AO3data()
    primaryTagData.searchURL = url
    primaryTagData.getTopInfo()
    primaryTagData.getNumWorks(True)
    return primaryTagData

def FetchMetaTags(tagName):
    print("fetching meta tags")

#    time.sleep(PAUSE_INTERVAL)
    url = getAO3TagStructureURL(tagName)
    tagData = AO3search.AO3data()
    tagData.metaURL = url
    tagData.getMetaTags()
    if DEBUG:
        print("Meta tags:")
        print(tagData.metaTags)
    return(tagData.metaTags)

###### FetchTop10ShipsAndFandoms
# fetches the top ships and fandoms in the Sort & Filter sidebar for a given tag
def FetchTop10ShipsAndFandoms(primaryTag, includeTags, excludeTags):
    print("fetching top 10 ships and fandoms")
#    time.sleep(PAUSE_INTERVAL)
    primaryTagData = FetchTopTagInfo(primaryTag, includeTags, excludeTags)
    return(primaryTagData.categories["relationship"]["top"], primaryTagData.categories["fandom"]["top"])


def AddNumWorksAndTopFandom(tag, include, exclude, minSize):
    tagDataWithoutRestrictions = FetchTopTagInfo(tag.name, [], [])
    if tagDataWithoutRestrictions.canonicalTagName != tag.name:
        tag.name = tagDataWithoutRestrictions.canonicalTagName

    tag.totalWorks = tagDataWithoutRestrictions.numworks
    try:
        unrestrictedFandoms = tagDataWithoutRestrictions.categories["fandom"]["top"]
        tag.topFandomOverall = getBiggestKeyByValue(unrestrictedFandoms)
    except:
        # this should never happen unless some tags are malformed
        tag.topFandomOverall = "(No fandoms)"

    if tag.totalWorks > minSize:    
        qualifyingTagData = FetchTopTagInfo(tag.name, include, exclude)
        tag.qualifyingWorks = qualifyingTagData.numworks
        try:
            qualifyingFandoms = qualifyingTagData.categories["fandom"]["top"]
            tag.topFandomQualifying = getBiggestKeyByValue(qualifyingFandoms)
        except:
            # this should never happen unless some tags are malformed
            tag.topFandomQualifying = "(No fandoms)"
    else:
        print("Ship total works (" + str(tag.totalWorks) + ") didn't surpass threshold size: " + str(minSize)) 
        tag.qualifyingWorks = -1 # we're not going to fetch this unless the tag qualifies; -1 signals we didn't bother
            
    tag.ratio = float(tag.qualifyingWorks)/float(tag.totalWorks)
    if DEBUG:
        print("Qualifying works: " + str(tag.qualifyingWorks) + "/" + str(tag.totalWorks) + " (" + str(round(100*tag.ratio)) + "%)")
    return tag

###### AddShip
# checks if a ship already exists in dictionary.  if not, adds a new Ship object and fetches data from AO3.
# Returns number of qualifying works (factoring in include/exclude restrictions)
def AddShip(shipName, include, exclude, pastShips, minShipSize):
#    print "~~~~~~adding Ship: " + shipName

    if shipName not in list(pastShips.keys()):
        ship = AddNewTagToDict(shipName, pastShips)
        ship = AddNumWorksAndTopFandom(ship, include, exclude, minShipSize)
        if ship.name != shipName:
            # the original ship name was non-canonical
            shipName = ship.name
            pastShips[shipName] = ship

        # if there is a meta tag, also add it
#        metas = FetchMetaTags(shipName)
#        for metaName in metas:
#            print "~~~~~ meta tag found: " + metaName
#            AddShip(metaName, include, exclude, pastShips)

    else:
        if DEBUG:
            print("~~~~~~ship previously found: " + shipName)
    return pastShips[shipName]

###### AddFandom
# checks if a fandom already exists in dictionary.  if not, adds a new Fandom object and fetches data from AO3.
# also adds all ships that aren't already in the ship dictionary.
# Returns number of qualifying works (factoring in include/exclude restrictions)
def AddFandomAndFetchNewCandidateFandoms(fandomName, include, exclude, pastFandoms, pastShips, minShipSize, candidateFandoms):
    print(".......................................Fandom deep dive: " + fandomName)
    if fandomName not in list(pastFandoms.keys()):
        # get the basic fandom stats
        fandom = AddNewTagToDict(fandomName, pastFandoms)
        fandom = AddNumWorksAndTopFandom(fandom, include, exclude, minShipSize)
        if fandom.name != fandomName:
            # the original fandom name was non-canonical
            fandomName = fandom.name
            pastFandoms[fandomName] = fandom


        # now get the info for all the ships -- unless the fandom is too small
#        if fandom.qualifyingWorks < minShipSize:
        if fandom.totalWorks < minShipSize:
            belowSizeThreshold = True
        else:
            belowSizeThreshold = False

        originalExcludeTags = exclude
        searchDepth = 1
        while not belowSizeThreshold:
#            print "FANDOM: " + fandomName + " recursion depth: " + str(recursionDepth)
            topS, topF = FetchTop10ShipsAndFandoms(fandomName, include, exclude)
            i = 1
            
            numBigShips = 0
            for shipName in topS:
                print("FANDOM DEEP DIVE: " + fandomName + "; depth " + str(searchDepth) + "; ship " + str(i) + "/" + str(len(topS)))
                ship = AddShip(shipName, include, originalExcludeTags, pastShips, minShipSize)
#                if ship.qualifyingWorks < minShipSize:
                if ship.totalWorks < minShipSize:
                    print("~~~ship below size threshold")
                    belowSizeThreshold = True
                else:
                    numBigShips += 1
                i += 1

            exclude = exclude + list(topS.keys())

            if numBigShips > 0:
                for subFandom in topF:
                    print("POSSIBLE NEW CANDIDATE FANDOM: " + subFandom) 
                    if subFandom in pastFandoms:
                        print("already gathered data on this fandom")
                    elif subFandom in candidateFandoms:
                        print("already a candidate")
                    else:
                        candidateFandoms.append(subFandom)
            
            searchDepth += 1

        # if there is a meta tag, also add it
#        metas = FetchMetaTags(fandomName)
#        for metaName in metas:
#           print "~~~~~ meta tag found: " + metaName
#            AddFandom(metaName, include, exclude, pastFandoms, pastShips, minShipSize)
    else:
        print("~~~~~~fandom previously found!")
        
    print("................................. Ending fandom deep dive: " + fandomName)
    try:
        return pastFandoms[fandomName]
    except:
        print("**** Fandom not added! " + fandomName)
        return None



def AddFandomDeprecated(fandomName, include, exclude, pastFandoms, pastShips, minShipSize, recurse):
    print(".......................................Fandom deep dive: " + fandomName)
    if fandomName not in list(pastFandoms.keys()):
        # get the basic fandom stats
        fandom = AddNewTagToDict(fandomName, pastFandoms)
        fandom = AddNumWorksAndTopFandom(fandom, include, exclude)
        if fandom.name != fandomName:
            # the original fandom name was non-canonical
            fandomName = fandom.name
            pastFandoms[fandomName] = fandom


        # now get the info for all the ships -- unless the fandom is too small
#        if fandom.qualifyingWorks < minShipSize:
        if fandom.totalWorks < minShipSize:
            belowSizeThreshold = True
        else:
            belowSizeThreshold = False

        originalExcludeTags = exclude
        searchDepth = 1
        while not belowSizeThreshold:
#            print "FANDOM: " + fandomName + " recursion depth: " + str(recursionDepth)
            topS, topF = FetchTop10ShipsAndFandoms(fandomName, include, exclude)
            i = 1
            
            if recurse:
                j=1
                for fandomName in topF:
                    print("FANDOM DEEP DIVE: " + fandomName + "; depth " + str(searchDepth) + "; fandom " + str(j) + "/" + str(len(topF)))
                    print("RECURSING...")
                    subFandom = AddFandom(fandomName, include, originalExcludeTags, pastFandoms, pastShips, minShipSize, False)
                    #                if subFandom.qualifyingWorks < minShipSize:
                    if subFandom.totalWorks < minShipSize:
                        print("~~~fandom below size threshold")
                        #                    belowSizeThreshold = True
                    j += 1
            
            for shipName in topS:
                print("FANDOM DEEP DIVE: " + fandomName + "; depth " + str(searchDepth) + "; ship " + str(i) + "/" + str(len(topS)))
                ship = AddShip(shipName, include, originalExcludeTags, pastShips)
#                if ship.qualifyingWorks < minShipSize:
                if ship.totalWorks < minShipSize:
                    print("~~~ship below size threshold")
                    belowSizeThreshold = True
                i += 1
            exclude = exclude + list(topS.keys())

            searchDepth += 1

        # if there is a meta tag, also add it
#        metas = FetchMetaTags(fandomName)
#        for metaName in metas:
#           print "~~~~~ meta tag found: " + metaName
#            AddFandom(metaName, include, exclude, pastFandoms, pastShips, minShipSize)
    else:
        print("~~~~~~fandom previously found!")
    try:
        return pastFandoms[fandomName]
    except:
        print("**** Fandom not added! " + fandomName)
        return None


# note: this OVERWRITES the file
def writeShipsToFile(ships, minSize, filename, discards):
    csv_discards = open(discards, 'w')
    with open(filename, 'w') as csv_ships:
        swriter = csv.writer(csv_ships)
        dwriter = csv.writer(csv_discards)
        swriter.writerow(["Ship", "Num works meeting requirements", "Top fandom meeting requirements", "Total works", "Top fandom overall", "Ratio of works meeting requirements"])
        dwriter.writerow(["Ship", "Num works meeting requirements", "Top fandom meeting requirements", "Total works", "Top fandom overall", "Ratio of works meeting requirements"])
        for key in sorted(ships, key = lambda name: ships[name].qualifyingWorks, reverse=True):
            s = ships[key]
#            if s.qualifyingWorks >= minSize:
            if s.totalWorks >= minSize:
                swriter.writerow([key, s.qualifyingWorks, s.topFandomQualifying, s.totalWorks, s.topFandomOverall, s.ratio])
            else:
                dwriter.writerow([key, s.qualifyingWorks, s.topFandomQualifying, s.totalWorks, s.topFandomOverall, s.ratio])


# note: this OVERWRITES the file
def writeFandomsToFile(fandoms, minSize, filename, discards):
    csv_discards = open(discards, 'w')
    with open(filename, 'w') as csv_fandoms:
        fwriter = csv.writer(csv_fandoms)
        dwriter = csv.writer(csv_discards)
        fwriter.writerow(["Fandom", "Num works meeting requirements", "Total works", "Ratio of works meeting requirements"])
        dwriter.writerow(["Fandom", "Num works meeting requirements", "Total works", "Ratio of works meeting requirements"])
        for key in sorted(fandoms, key = lambda name: fandoms[name].qualifyingWorks, reverse=True):
            f = fandoms[key]
#            if f.qualifyingWorks >= minSize:
            if f.totalWorks >= minSize:
                fwriter.writerow([key, f.qualifyingWorks, f.totalWorks, f.ratio])
            else:
                dwriter.writerow([key, f.qualifyingWorks, f.totalWorks, f.ratio])


###### PRIMARY FUNCTION: getTopShipsAndFandoms
# this is a function that can be called by other functions and returns
# a data object.  There's also a wrapper function at the end of the
# file that lets one call this from the command line and print results
# to CSV
def getTopShipsAndFandoms(primaryTag, includeTags, excludeTags, minShipSize, shipOut, fandomOut, shipDiscard, fandomDiscard):

    originalExcludeTags = excludeTags[:] #because we'll be adding more
    completeIncludeTags = includeTags
    completeIncludeTags.append(primaryTag)

    # these dictionaries are not guaranteed to be complete for the
    # smaller ships, but may also contain extras -- they are tracking
    # every ship and fandom ever investigated by the algorithm, some
    # of which are smaller than the min threshold
    topShips = {}
    topFandoms = {}
    smallestShip = sys.maxsize

    http = setupUrllib()

    candidateFandoms = []

    #MAX_DEPTH is a global variable set at beginning of this file.
    #This gives you the optional ability to govern how many times to
    #exclude previous ships & fandoms and repeat search
    for i in range(MAX_DEPTH):
        if DEBUG:
            print("*********** NEW BIG LOOP ITERATION: " + str(i))


        # write the files every time so we don't lose much data if the
        # program gets interrupted
        writeShipsToFile(topShips, minShipSize, shipOut, shipDiscard)
        writeFandomsToFile(topFandoms, minShipSize, fandomOut, fandomDiscard)

        if DEBUG:
            print("Smallest ship size: " + str(smallestShip))

        if smallestShip > minShipSize:
            fandoms = []
            ships = []
            iter = str(i+1)

            # fetch the tag page for the primary tag (e.g., "F/F")
#            time.sleep(PAUSE_INTERVAL)
            ships, fandoms = FetchTop10ShipsAndFandoms(primaryTag, includeTags, excludeTags)
            if DEBUG:
                print("including " + str(len(includeTags)) + " tags: ")
                print(includeTags)
                print("excluding " + str(len(excludeTags)) + " tags: ")
                print(excludeTags)
                print(" ")
                print(iter + ". fandoms")
                print(fandoms)
                print(iter + ". ships")
                print(ships)


            # Add new fandoms to candidate fandoms
            for fandomName in fandoms:
                candidateFandoms.append(fandomName)
                        
            #fetch data about each ship
            s = 1
            numShipsAboveThreshold = 0
            for shipName in ships:
#                time.sleep(PAUSE_INTERVAL)

                if DEBUG:
                    print("BIG LOOP ITERATION " + iter + "; SHIP " + str(s))

                ship = AddShip(shipName, completeIncludeTags, originalExcludeTags, topShips, minShipSize)
#                if ship.qualifyingWorks >= minShipSize:
                if ship.totalWorks >= minShipSize:
                    numShipsAboveThreshold += 1
                else:
                    #if DEBUG:
                    #    print "smaller than minShipSize"
#                    if ship.qualifyingWorks < smallestShip:
                    if ship.totalWorks < smallestShip:
#                        smallestShip = ship.qualifyingWorks
                        smallestShip = ship.totalWorks
                s += 1

            if DEBUG:
                print("*** Number of ships above size threshold: " + str(numShipsAboveThreshold))
            if numShipsAboveThreshold > 0:
                j = 1
                while candidateFandoms:
                    fandomName = candidateFandoms.pop()
                    if DEBUG:
                        print("Candidates: ")
                        print(candidateFandoms)
                        print("BIG LOOP ITERATION " + iter + "; FANDOM " + str(j) + "; " + str(len(candidateFandoms)) + " CANDIDATES REMAIN") 
                    fandom = AddFandomAndFetchNewCandidateFandoms(fandomName, completeIncludeTags, originalExcludeTags, topFandoms, topShips, minShipSize, candidateFandoms)
                    j += 1
                    writeShipsToFile(topShips, minShipSize, shipOut, shipDiscard)
                    writeFandomsToFile(topFandoms, minShipSize, fandomOut, fandomDiscard)


                # exclude just the top fandoms; don't want to exclude
                # the top ships because some of them may come from
                # fandoms that we haven't seen yet
                excludeTags = list(set().union(excludeTags,list(fandoms.keys())))
            else:
                print("********** no ships in this big loop surpassed size threshold!  Ending main fn.")
                break

            if DEBUG:
                print("********** FINISHING BIG LOOP ITERATION " + str(i))

        else:
            print("~~~~~~~~~~MinShipSize not surpassed. Ennding main fn.")
            break

    return(topShips, topFandoms)




def getTopShipsAndFandomsDeprecated(primaryTag, includeTags, excludeTags, minShipSize, shipOut, fandomOut, shipDiscard, fandomDiscard):

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
        # write the files every time so we don't lose much data if the
        # program gets interrupted
        writeShipsToFile(topShips, minShipSize, shipOut, shipDiscard)
        writeFandomsToFile(topFandoms, minShipSize, fandomOut, fandomDiscard)

        if smallestShip > minShipSize:
            fandoms = []
            ships = []
            iter = str(i+1)
            if DEBUG:
                print("*********** NEW BIG LOOP ITERATION: " + iter)

            # fetch the tag page for the primary tag (e.g., "F/F")
#            time.sleep(PAUSE_INTERVAL)
            ships, fandoms = FetchTop10ShipsAndFandoms(primaryTag, includeTags, excludeTags)
            if DEBUG:
                print("including " + str(len(includeTags)) + " tags: ")
                print(includeTags)
                print("excluding " + str(len(excludeTags)) + " tags: ")
                print(excludeTags)
                print(" ")
                print(iter + ". fandoms")
                print(fandoms)
                print(iter + ". ships")
                print(ships)


            #fetch data about each ship
            s = 1
            numShipsAboveThreshold = 0
            for shipName in ships:
#                time.sleep(PAUSE_INTERVAL)

                if DEBUG:
                    print("BIG LOOP ITERATION " + iter + "; SHIP " + str(s))

                ship = AddShip(shipName, completeIncludeTags, originalExcludeTags, topShips)
#                if ship.qualifyingWorks >= minShipSize:
                if ship.totalWorks >= minShipSize:
                    numShipsAboveThreshold += 1
                else:
                    #if DEBUG:
                    #    print "smaller than minShipSize"
#                    if ship.qualifyingWorks < smallestShip:
                    if ship.totalWorks < smallestShip:
#                        smallestShip = ship.qualifyingWorks
                        smallestShip = ship.totalWorks
                s += 1

            if DEBUG:
                print("*** Number of ships above size threshold: " + str(numShipsAboveThreshold))
            if numShipsAboveThreshold > 0:
                #fetch data about each fandom and all its top ships
                f = 1
                for fandomName in fandoms:
#                    time.sleep(PAUSE_INTERVAL)
                    if DEBUG:
                        print("BIG LOOP ITERATION " + iter + "; FANDOM " + str(f))
                    fandom = AddFandom(fandomName, completeIncludeTags, originalExcludeTags, topFandoms, topShips, minShipSize, True)
                    f += 1

                # exclude these ships and fandoms next time through the BIG LOOP
#                excludeTags = list(set().union(excludeTags,ships.keys(),fandoms.keys()))

                 # exclude just the top fandoms; don't want to exclude
                 # the top ships because some of them may come from
                 # fandoms that we haven't seen yet
                excludeTags = list(set().union(excludeTags,list(fandoms.keys())))
                writeShipsToFile(topShips, minShipSize, shipOut, shipDiscard)
                # don't include fandoms that don't cross min ship size
                writeFandomsToFile(topFandoms, minShipSize, fandomOut, fandomDiscard)
            else:
                print("********** no ships surpassed size threshold!  Ending main fn.")
                break

    return(topShips, topFandoms)

        
