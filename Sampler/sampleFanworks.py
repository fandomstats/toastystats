from bs4 import BeautifulSoup
import urllib3
import certifi
import re
import sys
import string
import csv
import time
from fanwork import Fanwork
from random import randint
from pprint import pprint

# CONSTRUCT PLATFORM-APPROPRIATE URL FN
def makeURL(platform, ID):
    if platform == "ao3":
        return("https://archiveofourown.org/works/" + str(ID))
    elif platform == "ffn":
        return("https://www.fanfiction.net/s/" + str(ID))
    elif platform == "wattpad":
        return("https://www.wattpad.com/story/" + str(ID))

# PRINT ALL FANWORK DATA TO CSV FN
def printCSV(outfile, fanworkDict):

    singleVars = ["URL", "platform", "title", "author", "firstPosted", "lastUpdated", "complete", "summary", "language", "rating", "words", "chapters", "hits", "kudos", "comments", "bookmarks", "follows", "inspiredBy"]
    listVars = ["fandom", "genre", "warning", "character", "category", "relationship", "freeform", "collections", "series"]

    with open(outfile, 'wb') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        
        # print header row (var names)
        wr.writerow(singleVars + listVars)

        for key in fanworkDict:
            fw = fanworkDict[key]
            row = []
            for sv in singleVars:
                value = getattr(fw, sv)
                row.append(value)
            for lv in listVars:
                listOfTags = getattr(fw, lv)
#                tagsAsString = ";".join(listOfTags)
                if listOfTags:
                    row.append(listOfTags)
                else:
                    row.append("")
            wr.writerow(row)

# STRIP PUNCTUATION AND ENCODE AS UTF
def stripPunct(s):
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in s if ch not in exclude)
    # make sure we've replaced commas in particular
#    s = re.sub(",", ";", s)
    s = s.encode('utf-8').strip()
    return s

# FIND A NUMBER IN A STRING
def findNum(s):
    try:
        return re.search(r'-?\d+\.?\d*', s).group()
    except:
        return "-1"

# FIND A DATE OF FORMAT month day, year
def findDate(s):
    s = stripPunct(s)
    try:
        return re.search(r'[\w]+[\s]*[\d]+[\s]*[\d]+', s).group()
    except:
        return "-1"

# SCRAPE ONE FANWORK FN: FFN
def getFFNInfo(soup, f):
    possibleGenres = ["Romance", "General", "Humor", "Drama", "Adventure", "Hurt/Comfort", "Angst", "Friendship", "Family", "Tragedy", "Fantasy", "Supernatural", "Horror", "Suspense", "Mystery", "Sci-Fi", "Parody", "Poetry", "Crime", "Spiritual", "Western"]

    for tag in soup.findAll("div"):
        # FANDOM
        if tag.has_attr('id') and tag['id'] == "pre_story_links":
            for child in tag.descendants:
                if child.name == 'a':
                    f.fandom = stripPunct(child.string)
        # SUMMARY
        if tag.has_attr('style') and tag['style'] == 'margin-top:2px':
            f.summary = stripPunct(tag.string)
            
    # get assorted metadata
    for tag in soup.findAll("span"):
        if tag.has_attr('class') and 'xcontrast_txt' in tag['class'] and 'xgray' in tag['class']:
            print(tag)
            for child in tag.descendants:
#                print "*&(&(*&(*&"
#                print child
                if child.name == "a":
                    # RATING
                    if child.has_attr('target'):
                        f.rating = child.string
                        metadata = re.findall(r'[^-]+', child.next_sibling)
#                        print metadata
                        # LANGUAGE
                        f.language = stripPunct(metadata[1])
                        for md in metadata:                            
#                            print md
                            try:
                                # GENRE(S)
                                if any(genre in md for genre in possibleGenres):
#                                    print "Genre! " + md
                                    f.genre = re.findall(r'[\w]+', md)
                                # CHAPTERS
                                elif "Chapters" in md:
                                    chapters = re.findall(r'[0-9,]+', md)
                                    f.chapters = stripPunct(chapters)
                                # WORDS
                                elif "Words" in md:
                                    words = re.findall(r'[0-9,]+', md)
                                    f.words = stripPunct(words)
                            except:
                                print("genre, chapters, or words error")
                    else:
                        # COMMENTS ("reviews")
                        f.comments = child.string
                        metadata = re.findall(r'[^-]+', child.next_sibling)
#                        print metadata
                        for md in metadata:
#                            print md
                            try:
                                # KUDOS ("favs")
                                if "Favs" in md:
                                    favs = re.findall(r'[0-9,]+', md)
                                    f.kudos = stripPunct(favs)
                                # FOLLOWS
                                elif "Follows" in md:
                                    follows = re.findall(r'[0-9,]+', md)
                                    f.follows = stripPunct(follows)
                            except:
                                print("favs/follows error")
                else:
                    # COMPLETE?
                    if "Status" in child:
                        if "Complete" in child:
                            f.complete = "True"
                        else:
                            f.complete = "False"
                    # PUBLISHED
                    if "Published" in child:
                        f.firstPosted = child.next_sibling.string
                    # UPDATED
                    elif "Updated" in child:
                        f.lastUpdated = child.next_sibling.string

# SCRAPE ONE FANWORK FN: WATTPAD
def getWattpadInfo(soup, f):
    for tag in soup.find("div", class_="author-info__username"):
        print("  ## AUTHOR ##  ")
        print(tag.string)
        f.author = tag.string

    for tag in soup.find("span", class_="table-of-contents__last-updated"):
        if tag.string != 'Last updated ':
            print("  ~~ LastUpdated ~~  ")
            print(tag.string)
            f.lastUpdated = tag.string

    for tag in soup.find("div", class_="icon completed"):
        print("  ~  Complete  ~  ")
        print(tag.string)
        f.complete = tag.string

    for tag in soup.findAll("pre"):
        print("  @@ SUMMARY @@  ")
        print(stripPunct(tag))
        f.summary = stripPunct(tag)
    
    tag = soup.find("div", class_="icon mature")
    if tag:
        print("  ++ Rating ++  ")
        print(tag.string)
        f.rating = tag.string

    for tag in soup.findAll("li", class_="stats-item", limit=3):
        print("  == Stats: reads, votes, parts ==  ")
        label = tag.find("span", class_="stats-label__text").string
        value = tag.find("span", class_="stats-value").string
        print(label + " = " + value)
        if label == "Reads":
            f.hits = value
        if label == "Votes":
            f.kudos = value
        if label == "Parts":
            f.chapters = value
    
    # get genres ("keywords")
    for tag in soup.findAll("meta", attrs={"name": "keywords"}):
        if tag.has_attr('name') and tag.has_attr('content'):
            print("  $$ GENRE $$  ")
            content = tag['content']
            content = stripPunct(content)
            print(content)
            f.genre = content

    # get freeform tags
    freeforms = []
    for tag in soup.findAll("ul", class_="tag-items"):
        if tag:
            print("  ### Tags ###  ")
            for t2 in tag.findAll("li"):
                freeforms.append(t2.string.encode('utf-8').strip())
            if freeforms:
                print(freeforms)
                f.freeform = ';'.join(freeforms)

def getTag(href):
    return href[9]

# SCRAPE ONE FANWORK FN: AO3
def getAO3Info(soup, f):

    if DEBUG: 
        print("Checkpoint 0")

    for ta in soup.findAll("textarea"):
        print("---&@&@&@&@&@&@&@&@&@&@&@&@&")
        print(ta)

    if DEBUG: 
        print("Checkpoint 1")

#    try:
#        for tag in soup.findAll("div", recursive=True):
#            if tag.has_attr('id'):
#                if "workskin" in tag['id']:
#                    wsTag = tag
#                    if DEBUG:
#                        print "Checkpoint 1.1"
#                        print "workskin ID: " + wsTag['id']
#                    for child in wsTag.descendants:
#                        if DEBUG:
#                            print "Checkpoint 1.2"
#                        if DEBUG:
#                            print child.name
#                        if child.has_attr('class'):
#                            if DEBUG:
#                                print "Checkpoint 1.3"
#                            print "child class: " + child['class']
#                            if DEBUG:
#                                print "Checkpoint 1.4"
#                            if "summary module" in child['class']:
#                                print "summary tag v1:"
#                                print child
#    except:
#        print "Failed to find workskin tag"

    if DEBUG: 
        print("Checkpoint 2")


    try:
        sumTag = soup.find(text="Summary:")
#    print "@&@&@&@&@&@&@&@&@&@&@&@&@&@&"
        if DEBUG:
            print("summary tag v2: " + sumTag)
    except:
        print("failed to find summary")

    if DEBUG: 
        print("Checkpoint 3")

    for dd in soup.findAll("dd"):
#        print "###########################"
#        print dd

        try:
            c = dd['class'][0]
        except:
            c = "no class"

        if DEBUG:
            print("Class:" + c)

#        if DEBUG: 
#            print "Checkpoint 3.1"
                            
        # special case published and updated variables (because I renamed them because they're confusing :P )
        if c == "published":
            f.firstPosted = dd.get_text()
        elif c == "updated":
            f.lastUpdated = dd.get_text()
        # find lists of tags, like warnings, etc. 
        elif "tags" in c:
            tags = []
            # get the beginning of the name, like "rating", "warning", "freeform"
            tagType = dd.partition(' ')[0]
            # now find all the actual tags
            for d in dd.descendants:
                if d.name == "a":
                    tags.append(a.get_text().encode('utf-8'))
            setattr(f, tagType, tags)
        # find single variables like kudos, words, etc.
        elif c != "no class":
            try:
                cleanedUp = dd.get_text().encode('utf-8').strip()
                setattr(f, c, cleanedUp)
            except:
                if DEBUG:
                    print("Exception -- trying to set value for: " + c)

#        if DEBUG: 
#            print "Checkpoint 3.2"
                            
    return


def validTitle(s):
    valid = "404" not in f.title and "Error" not in f.title and "User Session" not in f.title and "not found" not in f.title
#    if DEBUG:
#        print valid
    return(valid)

############# BEGIN MAIN FUNCTION

# basic error checking for right number of arguments
if len(sys.argv) < 5:
    sys.exit('Usage: %s [platform] [num work IDs to sample] [max work ID] [outfile] (e.g.: %s "Wattpad" 100 1903351 "wattpad.csv")\n' % (sys.argv[0],sys.argv[0]))

platform, numworks, maxID, outfile = sys.argv[1:5]

platform = string.lower(platform)
numworks = int(numworks)
maxID = int(maxID)
DEBUG = 1

fanworkDict = {}
#funcDict = {
#    'ao3': "getAO3FanworkInfo",
#    'ffn': "getFFNFanworkInfo",
#    'wattpad': "getWattpadFanworkInfo"
#}

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

# sample the fanwork
for i in range(0, numworks):
    if DEBUG: 
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("fetching work " + str(i+1))
    # pause to avoid inadvertant DOS attack
    time.sleep(2)

    # get the fanwork ID and convert to a URL 
    workID = randint(1, maxID)
    workURL = makeURL(platform, workID)
    f = Fanwork(workURL, platform)
    fanworkDict[workID] = f

    # fetch the HTML
    try:
        r = http.request('GET', workURL, headers={'Accept-Encoding': 'gzip'})
    except:
#        print r.status
        print("Bad URL: " + workURL)
        continue

    try:
        soup = BeautifulSoup(r.data, "html.parser")
        soup.prettify()
    except:
        print("Couldn't prettify")
        continue

    # get the title (same for all platforms)
    try:
        title = soup.find_all('title')[0]
        f.title = title.get_text().encode('utf-8').replace("\n", "").replace(",", ";")
    except:
        title = 'Error'

    if validTitle(f.title):
        try:
            if platform == "ao3":
                getAO3Info(soup, f)
            elif platform == "wattpad":
                getWattpadInfo(soup, f)
            elif platform == "ffn":
                getFFNInfo(soup, f)
        except:
            print("work error")
    if DEBUG:
#        for key in fanworkDict:
#        print key

        pprint(vars(f))

printCSV(outfile, fanworkDict)
#        f = fanworkDict[key]
#        print f.URL
#        print f.title
#        print "First posted: " + f.firstPosted
#        print "Last updated: " + f.lastUpdated
#        print "Words: " + f.words
#        print "Hits: " + f.hits
#        print "Kudos: " + f.kudos
#        print "Comments: " + f.comments
#        print "Words: " + f.words
#        print "Bookmarks: " + f.bookmarks
#        print "Chapters: " + f.chapters
#        print "Language: " + f.language
        

#fn: outputCSV (same for all)




# reformat the media type string into the AO3 URL format 
#url = "http://archiveofourown.org/media/" + category + "/fandoms"

# grab all the fandoms and numbers of fanworks
#fandominfo = soup.find_all('li')
#for fi in fandominfo:
    # separate out the fandom name and the number of fanworks
#    matchObj = re.search( r'<a class=\"tag\".*>(.*)</a>.*\(([0-9]+)\)', str(fi), re.I|re.S)
#    if matchObj:
#        fandom = matchObj.group(1)
#        numworks = int(matchObj.group(2))
        # print out the fandom and num works if they pass the threshold
#        if numworks >= threshold:
            #reformat special characters in fandom name
#            fandom = re.sub(r'&amp;', r'&', fandom)
#            print fandom + ", " + str(numworks)

