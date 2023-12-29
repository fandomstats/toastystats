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

numArgs = 4
args = getArguments(sys.argv, numArgs, 'Usage: topCharacterStats [character names file] [include tags file] [exclude tags file] [outfile] (e.g.: topCharacterStats "characterNames.txt" "include.tags" "exclude.tags" "characters.csv"")\n')

if DEBUG:
    print(args)

tag, includefile, excludefile, charOut = args[0:numArgs]
recursionDepth = int(recursionDepth)

includeTags = []
excludeTags = []

includeTags = [line.rstrip('\n') for line in open(includefile)]
excludeTags = [line.rstrip('\n') for line in open(excludefile)]

http = setupUrllib()

# for each character:
# get num works for this character
# get their primary fandom
# get num works with the include and exclude tags
