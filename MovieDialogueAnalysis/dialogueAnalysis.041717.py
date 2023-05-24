import sys
import csv
import time
import pdb
import AO3search
import createAO3TagURL 
import createAO3SearchURL
import Levenshtein
import string
import importlib

# try to fix the damn issues with non-ASCII characters
importlib.reload(sys)  
sys.setdefaultencoding('utf8')

NUMARGS = 5
PAUSE = 2
MIN_AO3_MOVIE_RESULTS = 50 #if a search for the movie title doesn't
                           #return this many results on AO3, don't
                           #bother to fetch character info
moviesWithFewAO3Results = {} # store the ones that are too small here

TagURL = createAO3TagURL.TagURL
FandomSearchURL = createAO3SearchURL.FandomSearchURL

movieDict = {}
characters = []

class Character:
    age = None
    gender = None
    words = 0
    fractionOfDialogue = 0.0
    numWorks = 0  #fanworks on AO3
    titleSimilarity = 0
    fandomNumWorks = 0
    fractionOfFanworks = 0.0
    closestFandom = ''
    def __init__(self, name, movieID):
        self.name = name
        # Character contains a pointer to a Movie
        if movieID in movieDict:
            self.movie = movieDict[movieID]
        else:
            self.movie = Movie(movieID)
        # update the Movie object to contain pointer to Character
        movie.characters.append(self)

class Movie:
    year = None
    scriptID = None
    imdbID = None
    title = None
    totalWords = 0
    gross = 0
    characters = []
    def __init__(self, id):
        self.scriptID = id  
        movieDict[id] = self

def longestSubstringFinder(string1, string2, caseInsensitive):
    if caseInsensitive:
        string1 = string1.lower()
        string2 = string2.lower()
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer


if len(sys.argv) < NUMARGS:
    sys.exit('Usage: %s character_list character_map meta_data outfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > NUMARGS:
    arg = sys.argv[NUMARGS]
    if arg == "-verbose" or arg == "-v":
        verbose = True

charlistfile = sys.argv[1]
charmapfile = sys.argv[2]
metafile = sys.argv[3]
outfile = sys.argv[4]

# open output file, set buffer to 1 (flush every line) and print output header
outfp = open(outfile, 'w', 1)
outfp.write("name, movie, percent of dialogue, percent of fanworks, age, gender,  year, script ID, imdb ID, movie words, gross, AO3 works, AO3 fandom, title similarity\n")

# READ IN THE CSV FILES
try:
    clfp = open(charlistfile, "rb")
    cmfp = open(charmapfile, "rb")
    mefp = open(metafile, "rb")
    charlist = csv.DictReader(clfp)
    charmap = csv.DictReader(cmfp)
    metadata = csv.DictReader(mefp)
except ValueError:
    print("File read failed!")


# read in movie metadata into movieDict
if verbose:
    print("reading in movie data...")

for row in metadata:
    scriptID = row['script_id']
    movie = None
    if scriptID in movieDict:
        movie = movieDict[scriptID]
    else:
        movie = Movie(scriptID)
    movie.imdbID = row['imdb_id']
    movie.title = row['title']
    movie.year = row['year']
    if row['gross']:
        movie.gross = int(row['gross'])
    else:
        movie.gross = None
#    movie.linesdata = row['lines_data']
#    if verbose:
#        print movie.title
#        print movie.year
#        print movie.gross

if verbose:
    print("reading in character data...")

# read in the character stats, and link to the matching movies
for charStats in charlist:
    charName = charStats['imdb_character_name']
    scriptID = charStats['script_id']
    c = Character(charName, scriptID)
    c.gender = charStats['gender']
    c.words = int(charStats['words'])
    # update the number of words in the movie
    c.movie.totalWords = c.movie.totalWords + c.words
    try:
        c.age = int(charStats['age'])
    except:
        c.age = None
    characters.append(c)
#    if verbose:
#        print "num characters processed: ", len(characters)

# calculate the percent of words each character has
for c in characters:
    c.fractionOfDialogue = float(c.words) / float(c.movie.totalWords)


# and now to find the AO3 data and print to CSV...

for c in characters:
    print("**********************************")
    print("Fetching AO3 data for", c.name, "(", c.movie.title, ")")

    # first make sure that searching for the movie title on AO3
    # returns some fanworks
    numResults = 0
    if c.movie.title in moviesWithFewAO3Results:
        numResults = moviesWithFewAO3Results[c.movie.title]
    else:
        movieData = AO3search.AO3data()
        bareTitle = c.movie.title.translate(None, string.punctuation)
        # in case of a movie like Alien^3 with encoding errors...
        bareTitle = str(bareTitle, errors='ignore')
        movieData.searchURL = FandomSearchURL(bareTitle, verbose)
        numResults = movieData.getNumWorks(False)

    if verbose:
        print("Num works returned for movie:", numResults)

    if numResults < MIN_AO3_MOVIE_RESULTS:
        moviesWithFewAO3Results[c.movie.title] = numResults
        c.numWorks = -1
    else:
        # grab the AO3 data for this character tag (will also include
        # characters with the same name)

        # pause so as not to DOS attack AO3!
        time.sleep(PAUSE)

        url = TagURL(c.name, 'works', verbose)
        if verbose:
            print("Character:", c.name)
            print("Movie:", c.movie.title)
            print("Age (actor):", c.age)
            print("Gender:", c.gender)
            print("Words:", c.words)
            print("Fraction of dialogue:", c.fractionOfDialogue)
            print("URL:", url)
            ao3data = AO3search.AO3data()
            ao3data.searchURL = url
            try:
                ao3data.getTopInfo()
                fandoms = ao3data.categories['fandom']['top']
#                if verbose:
#                    print fandoms
            except:
                print("AO3 fetch failed")

        # now try to find the right fandom amongst this character's top10 fandoms
        canonTitle = c.movie.title 
        print("Canonical title:", canonTitle)
        closestMatch = ''
        biggestRatio = 0
        numworks = 0
        for f in fandoms:

            # see: http://stackoverflow.com/questions/14260126/how-python-levenshtein-ratio-is-computed
            longestSubstring = longestSubstringFinder(str(canonTitle), str(f.encode('utf-8')), True)
            substringSim = float(len(longestSubstring)) / float(max(len(str(canonTitle)), len(str(f.encode('utf-8')))))
            levSim = Levenshtein.ratio(str(canonTitle), str(f.encode('utf-8')))
            levSim = levSim / float(max(len(str(canonTitle)), len(str(f.encode('utf-8')))))
            if verbose:
                #            print levSim
                print(substringSim, f)
#                print longestSubstring
                sim = substringSim
                if sim > biggestRatio:
                    biggestRatio = sim
                    closestMatch = f
                    numworks = fandoms[f]
        c.closestFandom = closestMatch.encode('utf-8')
        c.titleSimilarity = biggestRatio
        c.numWorks = numworks
        if verbose:
            print("closest Fandom:", c.closestFandom, ",", c.numWorks) 

    # if we found an acceptable fandom match, find total words in fandom
        if c.titleSimilarity > 0:
            url = TagURL(c.closestFandom, 'works', verbose)
            fandomData = AO3search.AO3data()
            fandomData.searchURL = url
            try:
                fandomData.getNumWorks(True)
                fandomData.numworks = max(fandomData.numworks, 0)
                if verbose:
                    print("Num fandom works:", fandomData.numworks)
                    print(url)
            except:
                print("AO3 numworks fetch failed", url)

            c.fandomNumWorks = fandomData.numworks
            if(c.fandomNumWorks > 0):
                c.fractionOfFanworks = float(c.numWorks) / float(c.fandomNumWorks)
                if verbose:
                    print("Fraction of works:", c.fractionOfFanworks)

# print output row
    newrow = [c.name, c.movie.title, str(c.fractionOfDialogue), str(c.fractionOfFanworks), str(c.age), c.gender, str(c.movie.year), str(c.movie.scriptID), c.movie.imdbID, str(c.movie.totalWords), str(c.movie.gross), str(c.numWorks), c.closestFandom, str(c.titleSimilarity)]
    outfp.write(','.join(newrow))
    outfp.write('\n')


outfp.close()
