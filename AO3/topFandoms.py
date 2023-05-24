from bs4 import BeautifulSoup
import urllib3
#import urllib
#import urllib.parse
import re
import sys
from toastyTools import getSoupFromURL

# VARIABLES WE MAY WANT TO CHANGE
minFandomSize = 500
mediaCategories = ["Books & Literature", "Celebrities & Real People", "Music & Bands", "Theater", "Video Games", "Anime & Manga", "Cartoons & Comics & Graphic Novels", "Movies", "Other Media", "TV Shows"]
umbrellaTerms = ["Related Fandoms", "All Media Types", "Marvel Cinematic Universe", "DCU", "Jossverse", "Ambiguous Fandom", "Bandom", "K-pop", "Jpop", "Jrock", "Music RPF", "Actor RPF", "Sports RPF", "Blogging RPF", "Real Person Fiction", "Internet Personalities", "- Works", "Video Games", "MS Paint Adventures"]

# TAKE IN COMMAND LINE ARGUMENTS
if len(sys.argv) < 3:
    sys.exit('Usage: %s <num top fandoms> <include umbrella fandoms?> (e.g.: %s 50 True)' % (sys.argv[0],sys.argv[0]))

numFandoms = int(sys.argv[1])
includeUmbrellaFandoms = eval(sys.argv[2]) 
fandomsByCategory = {}
topFandoms = {}

for category in mediaCategories:
    print("Fetching " + category)

    # SET UP THE DICTIONARY FOR THIS CATEGORY
    fandomsByCategory[category] = {}

    # FETCH THE AO3 PAGE WITH ALL THE FANDOMS FOR THIS CATEGORY
    modifiedCategory = category.replace(" ", "%20")
    modifiedCategory = modifiedCategory.replace("&", "*a*")
    url = "http://archiveofourown.org/media/" + modifiedCategory + "/fandoms"
    soup = getSoupFromURL(url)

    # ITERATE THROUGH ALL FANDOMS LISTED ON THE PAGE AND SAVE THEIR NAMES AND SIZES
    fandominfo = soup.find_all('li')
    for fi in fandominfo:
        matchObj = re.search( r'<a class=\"tag\".*>(.*)</a>.*\(([0-9]+)\)', str(fi), re.I|re.S)
        if matchObj:
            fandom = matchObj.group(1)
            # IF IT PASSES A THRESHOLD...
            numworks = int(matchObj.group(2))
            if numworks >= minFandomSize:
#                print "%s: %d" % (fandom, numworks)
                # PUT IT IN THE CATEGORY DICTIONARY
                if includeUmbrellaFandoms:
                    fandomsByCategory[category][fandom] = numworks
                else:
                    # IGNORE THE UMBRELLA FANDOMS
                    isUmbrella = False
                    if fandom == "Marvel":
                        isUmbrella = True
                    for u in umbrellaTerms:
#                        print "%s in %s? %s" % (u, fandom, u in fandom)
                        if u in fandom:
                            isUmbrella = True
                    if not(isUmbrella):
                        fandomsByCategory[category][fandom] = numworks


# DISPLAY THE TOP FANDOMS PER CATEGORY
for category in sorted(mediaCategories):
    print("TOP FANDOMS: %s" % category)
    catFandoms = fandomsByCategory[category]
    i = 1
    for key, value in sorted(iter(catFandoms.items()), key=lambda k_v: (k_v[1],k_v[0]), reverse=True):
         print("%d, %s, %s" % (i, key, value))
         # PUT IT IN THE TOP FANDOM DICTIONARY
         topFandoms[key] = value
         if i >= numFandoms:
             break
         i = i+1

    print(" ")

# DISPLAY THE TOP FANDOMS OVERALL
i = 1
print("TOP FANDOMS OVERALL")
for key, value in sorted(iter(topFandoms.items()), key=lambda k_v1: (k_v1[1],k_v1[0]), reverse=True):
    print("%d, %s, %s" % (i, key, value))
    if i >= numFandoms:
        break
    i = i+1

