import sys
import string
from getTopShipsAndFandomsLibrary import getTopShipsAndFandoms
from toastyTools import getArguments


############# BEGIN WRAPPER FUNCTION

args = getArguments(sys.argv, 8, 'Usage: topShipsAndFandoms [primary tag] [include tags file] [exclude tags file] [min ship size] [ship outfile] [fandom outfile] [ships that are too small outfile] [fandoms that are too small outfile] (e.g.: topShipsAndFandoms "F/F" "include.tags" "exclude.tags" 100 "ships.csv" "fandoms.csv" "discardedShips.csv" "discardedFandoms.csv")\n')

tag, includefile, excludefile, minShipSize, shipOut, fandomOut, shipDiscards, fandomDiscards = args[0:9]
minShipSize = int(minShipSize)

includeTags = [line.rstrip('\n') for line in open(includefile)]
excludeTags = [line.rstrip('\n') for line in open(excludefile)]

ships, fandoms = getTopShipsAndFandoms(tag, includeTags, excludeTags, minShipSize, shipOut, fandomOut, shipDiscards, fandomDiscards)
