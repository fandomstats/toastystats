import sys
from toastyTools import getArguments, mergeDictionaries
from getTopShipsAndFandomsLibrary import getTopShipsAndFandoms, writeShipsToFile

args = getArguments(sys.argv, 2, 'Usage: topShipsOnAO3 [min ship size] [outfile] (e.g.: topShipsOnAO3 1000 ships.csv)\n')

minShipSize, shipOut = args[0:3]
minShipSize = int(minShipSize)
topShips = {}

# because every work has exactly one ratings tag, we'll fetch the top ships for each and then combine
ratingsTags = ["Not Rated", "General Audiences", "Teen And Up Audiences", "Mature", "Explicit"]

for r in ratingsTags:
    print "!!!!!!!!!!!!!!!!!!!!!!!! FETCHING SHIPS FOR RATING TAG: " + r
    rShipsOut = r + "-ships-tmp.csv"
    rFandomsOut = r + "-fandoms-tmp.csv"
    ships, fandoms = getTopShipsAndFandoms(r, [], [], minShipSize/len(ratingsTags), rShipsOut, rFandomsOut)

    # we don't actually want to have a subset of these labeled "qualifyingWorks,"
    # because the output of this function is not related to individual ratings tags
    # (they're just a means to a end) so fix that
    for ship in ships.values():
        ship.qualifyingWorks = ship.totalWorks
        ship.ratio = 1

    topShips = mergeDictionaries(topShips, ships)


writeShipsToFile(topShips, minShipSize, shipOut)
