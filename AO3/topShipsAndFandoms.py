import sys
import string
from getTopShipsAndFandomsLibrary import getTopShipsAndFandoms
from toastyTools import getArguments


############# BEGIN WRAPPER FUNCTION

args = getArguments(sys.argv, 6, 'Usage: topShipsAndFandoms [primary tag] [include tags file] [exclude tags file] [min ship size] [ship outfile] [fandom outfile] (e.g.: topShipsAndFandoms "F/F" "include.tags" "exclude.tags" 100 "ships.csv" "fandoms.csv")\n')

tag, includefile, excludefile, minShipSize, shipOut, fandomOut = args[0:7]
minShipSize = int(minShipSize)

includeTags = [line.rstrip('\n') for line in open(includefile)]
excludeTags = [line.rstrip('\n') for line in open(excludefile)]

ships, fandoms = getTopShipsAndFandoms(tag, includeTags, excludeTags, minShipSize, shipOut, fandomOut)
