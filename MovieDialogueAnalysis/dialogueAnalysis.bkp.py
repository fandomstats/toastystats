import sys
#import importJSON
#import AO3search
import csv
import time
import pdb

NUMARGS = 4

movieDict = {}
characters = []

class Character:
    age = None
    gender = None
    words = 0
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


if len(sys.argv) < NUMARGS:
    sys.exit('Usage: %s character_list character_map meta_data [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > NUMARGS:
    arg = sys.argv[NUMARGS]
    if arg == "-verbose" or arg == "-v":
        verbose = True

charlistfile = sys.argv[1]
charmapfile = sys.argv[2]
metafile = sys.argv[3]

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


# 'transpose' metadata so it's rows indexed by scriptID
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
    if verbose:
        print(movie.title)
        print(movie.year)
        print(movie.gross)


# read in the character's stats, and find the matching full name & movie title
for charStats in charlist:
    charName = charStats['imdb_character_name']
    scriptID = charStats['script_id']
    c = Character(charName, scriptID)
    c.gender = charStats['gender']
    c.words = int(charStats['words'])
    try:
        c.age = int(charStats['age'])
    except:
        c.age = None
    characters.append(c)
    if verbose:
        print("Character:", c.name)
        print("Movie:", c.movie.title)
        print("Age (actor):", c.age)
        print("Gender:", c.gender)
        print("Words:", c.words)
        print("num characters: ", len(characters))

