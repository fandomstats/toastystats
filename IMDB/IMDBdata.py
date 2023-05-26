import sys
import convert
import re
from bs4 import BeautifulSoup
import urllib3
import pdb
import UnicodeToURL


class IMDBdata:
    # ********* DATA FIELDS
    showname = ''
    showSearchURL = ''
    showURL = ''
    htmlData = {}
    IMDBTopCast = {}
#    AO3TopCharacters = {}

    # ********* METHODS
    def __init__(self, showname):
        self.showname = showname
    
    # METHOD: fetchHTML
    def fetchHTML(self):
        if self.htmlData == {}:            
            http = urllib3.PoolManager()
            r = {}
        #try:
         #   r = http.request('GET', self.searchURL)
          #  soup = BeautifulSoup(r.data)
           # soup.prettify()                
            #self.htmlData = soup
            #return soup
        #except:
         #   print "ERROR: failure to fetch URL: ", self.searchURL
        else:
            return self.htmlData
            
#METHOD: createURL
    def createURL(self, startyear, endyear):
        if self.showname == '':
            print("ERROR: no show name")
        else:
            tmpname = re.sub('\s', '%20', self.showname)
            showSearchURL = "http://www.imdb.com/search/title?release_date=" + startyear + "," + endyear + "&title=" + tmpname + "&title_type=tv_series"

    # METHOD: getTopCastInfo -- scrape the top cast info
#    def getTopCastInfo(self):





