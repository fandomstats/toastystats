from IMDBdata import *
import sys

# get the top cast info and other basic info for a TV show on IMDB

########## PARAMETERS

startdate = 1990
enddate = 2015



if len(sys.argv) < 3:
    sys.exit('Usage: %s showlist_textfile outfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 3:
    arg = sys.argv[3]
    if arg == "-verbose" or arg == "-v":
        verbose = True


showfile = sys.argv[1]
csvfile = sys.argv[2]

fi = open(showfile, "r")


for show in fi:
    showdata = IMDBdata(show)

    if verbose:
        print("Show: ", showdata.showname)

    IMDBdata.createURL(startdate, enddate)
    
    if verbose:
        print("URL: ", showdata.showSearchURL)

#fo = open(csvfile, "w")


