from bs4 import BeautifulSoup
import urllib3
import re
import sys
from toastyTools import getSoupFromURL

#def getNum(url):

if len(sys.argv) < 2:
    sys.exit('Usage: %s AO3_search_url [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 2:
    arg = sys.argv[2]
    if arg == "-verbose" or arg == "-v":
        verbose = True

url = sys.argv[1]

if verbose:
    print("fetching page: ", url)

soup = getSoupFromURL(url)    

# extract the number of works returned by this search
tag = soup.find_all(text=re.compile("Works( found)* in"))
if verbose:
    print(tag)
    print("Number of H2 tags found: ", len(tag))

try:
    line =  tag[0]
except:
    total = -1
    if verbose:
        print("no H2 tags found")
    print(total)
    sys.exit()

nums = re.findall('([0-9]+)', line)

if len(nums) == 0:
    total = -1
    if verbose:
        print("No numbers found in H2 tag content: ", line)
elif len(nums) == 1:
    total = nums[0]
else: 
    total = nums[2]

if verbose:
    print("Number of works: ", total)

print(total)
#    return total
