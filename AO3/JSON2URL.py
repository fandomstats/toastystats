import json
import sys
import convert

if len(sys.argv) < 2:
    sys.exit('Usage: %s JSON_file [-verbose]' % sys.argv[0])

verbose = False

# get cmd line args
if len(sys.argv) > 2:
    arg = sys.argv[2]
    if arg == "-verbose" or arg == "-v":
        verbose = True

filename = sys.argv[1]

if verbose:
    print("filename: ", filename)

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


for s in searches:
    if verbose:
        print("search: ", s)

    params = ''

    # fetch the category(ies)
    c = ''        
    try:
        c = s['category']
        tmp = convert.convertToAO3(c, 'cat', verbose)
        c = tmp[0]
        params += tmp[1]
        params += ', '
        if verbose: 
            print("category: ", c)
            print("params ", params)
    except:
        if verbose: 
            print("no category in search ", s)

    # fetch the warning(s)
    w = ''        
    try:
        w = s['warning']
        tmp = convert.convertToAO3(w, 'warn', verbose)
        w = tmp[0]
        params += tmp[1]
        params += ', '
        if verbose: 
            print("warning: ", w)
            print("params ", params)
    except:
        if verbose: 
            print("no warning in search ", s)

    # fetch the tag(s)
    t = '&tag_id='
    try:
        tag = s['tag']
        tmp = convert.convertToAO3(tag, 'tag', verbose)    
        t += tmp[0]
        params += tmp[1]
        params += ', '
        if verbose: 
            print("tag: ", t)
            print("params ", params)
    except:
        if verbose: 
            print("no tag in search ", s)

    # fetch the "search within results"
    swr = '&work_search%5Bquery%5D='
    try:
        wth = s['search within results']
        tmp = convert.convertToAO3(wth, 'within', verbose)    
        swr += tmp[0]
        params += tmp[1]
        params += ', '
        if verbose: 
            print("search within results: ", swr)
            print("params ", params)
    except:
        if verbose: 
            print("no search within results in search ", s)

    # assemble the URL
    urlprefix = 'http://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at'
    urlprequery = '&work_search%5Bother_tag_names%5D='
    urlpretag = '&work_search%5Blanguage_id%5D=&work_search%5Bcomplete%5D=0'

    u = urlprefix + c + w + urlprequery + swr + urlpretag + t
    if verbose: 
        print('***********')
    print(u)
    if verbose: 
        print('***********')

