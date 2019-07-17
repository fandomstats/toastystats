import csv

class Fanwork:

    platform = ""
    title = ""
    author = ""
    firstPosted = ""
    lastUpdated = ""
    complete = ""
    summary = ""
    language = ""
    rating = ""
    words = "" # AO3 and FFN
    chapters = "" # AO3, FFN, Wattpad ("parts")
    hits = "" # AO3 and Wattpad ("reads")
    kudos = "" # AO3, FFN ("favs"), Wattpad ("votes")
    comments = "" # AO3, FFN ("reviews") -- not currently available on Wattpad
    bookmarks = "" # AO3
    follows = "" # FFN
    inspiredBy = "" # AO3
    fandom = [] # AO3 and FFN
    genre = [] # FFN and Wattpad
    warning = [] # AO3 
    character = [] # AO3 and FFN 
    category = [] # AO3 
    relationship = [] # AO3 
    freeform = [] # AO3 and Wattpad
    collections = [] # AO3
    series = [] # AO3


    # INIT FN
    def __init__(self, URL, platform):
        self.URL = URL
        self.platform = platform


