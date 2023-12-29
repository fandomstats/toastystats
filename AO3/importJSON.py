import json
import sys
import convert
import AO3search

# takes in a JSON filename and returns a list of AO3data objects containing the search specifications 
def importFile(filename, verbose):

    # load JSON from file
    try:
        with open(filename) as f:
            j = json.load(f)
    except:
        sys.exit("could not load JSON file")

    try:
        searches = j['searches']
    except:
        sys.exit("No 'searches' field in file")

    AO3datalist = [];

    for s in searches:
        if verbose:
            print("search: ", s)
            
        x = AO3search.AO3data()
        x.searchParams = s
        AO3datalist.append(x)


    return AO3datalist
