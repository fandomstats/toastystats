from bs4 import BeautifulSoup
import urllib3
import re
from toastyTools import getSoupFromURL

url = "http://archiveofourown.org/media/TV%20Shows/fandoms"

soup = getSoupFromURL(url)


showinfo = soup.find_all('li')
#print str(showinfo[0])
for si in showinfo:
#    matchObj = re.match( r'<a.*>(.*)</a> 
    matchObj = re.search( r'<a class=\"tag\".*>(.*)</a>.*\(([0-9]+)\)', str(si), re.I|re.S)
    if matchObj:
        fandom = matchObj.group(1)
        if not re.search(r'All Media Types', fandom, re.I):
            if not re.search(r'Related Fandoms', fandom, re.I):
                numworks = int(matchObj.group(2))
                if numworks > 500:
                    print(fandom + ", " + str(numworks))
