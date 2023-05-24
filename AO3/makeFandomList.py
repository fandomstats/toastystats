from bs4 import BeautifulSoup
import urllib3
import re
import sys
import time
import os
#import toastytools
from toastyTools import getSoupFromURL


if len(sys.argv) < 2:
    sys.exit('Usage: %s URLfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 2:
    arg = sys.argv[2]
    if arg == "-verbose" or arg == "-v":
        verbose = True

urlfile = sys.argv[1]

if verbose:
    print("reading file: ", urlfile)

try:
    with open(urlfile) as f:
        urls = f.readlines()
except:
    sys.exit("could not read URL file")

if verbose:
    print("Number of lines: ", len(urls))

fandomNames = []
for u in urls:
    if verbose:
        print("******\n")

    u = u.rstrip('\n')

    if verbose:
        print("fetching page: ", u)

    if verbose:
        print("Pausing so as not to DOS AO3...")
    
    soup = getSoupFromURL(u)

    
    # extract the fandom names
    tmpList = soup.findAll("a", {"class" : "tag"})

    #just grab the text part
    for link in tmpList:
        print(link.text.encode('utf-8'))

