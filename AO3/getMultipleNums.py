import sys
import time
import os

#def getNum(url):

if len(sys.argv) < 2:
    sys.exit('Usage: %s URLfile [-verbose]' % sys.argv[0])

verbose = False

if len(sys.argv) > 2:
    arg = sys.argv[2]
    if arg == "-verbose" or arg == "-v":
        verbose = True

urlfile = sys.argv[1]

if verbose:
    print("reading file: ", urlfile)

try:
    with open(urlfile) as f:
        urls = f.readlines()
except:
    sys.exit("could not read URL file")

if verbose:
    print("Number of lines: ", len(urls))

for u in urls:
    if verbose:
        print("******\n")

    u = u.rstrip('\n')


    if verbose:
        cmd = 'python getNum.py "' + u + '" -v'
    else:
        cmd = 'python getNum.py "' + u + '"' 

    if verbose:
        print("cmd: ", cmd)

    try:
        os.system(cmd)
    except:
        sys.exit("could not call getNum.py")
