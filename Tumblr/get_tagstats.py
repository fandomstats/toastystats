#!/usr/bin/python

import pytumblr, sys, re, operator, datetime 
import importlib
importlib.reload(sys)
sys.setdefaultencoding("utf-8")

### SUBROUTINES

def addtocount(item, counter):
#    print "addtocount: " + str(item) 
    if item in counter:
#        print "count = " + str(counter[item])
        counter[item] = counter[item] + 1
    else:
#        print "count = 1"
        counter[item] = 1

def printpair(item, count, f):
#    print "printpair"
    f.write(item + ", " + str(count) + "\n")

def printall(typecount, tagcount, datecount, hourcount, threshold, outfile):

#    print "printall"
    f = open(outfile, 'w')

    f.write("******* TYPES:\n")
    sorttype = sorted(iter(typecount.items()), key=operator.itemgetter(1), reverse=True)
    for st in sorttype:
         printpair(st[0], st[1], f)

    f.write("\n\n******* DATES:\n")
    dates = sorted(datecount.keys())
    for d in dates:
         printpair(str(d), datecount[d], f)

    f.write("\n\n******* HOURS:\n")
    for hour in hourcount:
         printpair(str(hour), hourcount[hour], f)

    f.write("\n\n******* TAGS:\n")
    sorttag = sorted(iter(tagcount.items()), key=operator.itemgetter(1), reverse=True)
    for st in sorttag:
        if st[1] >= threshold:
                printpair(st[0], st[1], f)

    f.close()

def trytoprint(r, name, f):
#    print "trytoprint"
    try: 
        f.write(str(r[name]))
    except:
        print("couldn't write ", name)
#        print r
    f.write(", ")


def printpost(postdata, outfile):
#    print "printpost"
    r = postdata
    try:
        f = open(outfile, 'a')
    except:
        print("couldn't open outfile")
        return None
#    print 'trying to print post to outfile'

    trytoprint(r, 'id', f)
    trytoprint(r, 'blog_name', f)
    trytoprint(r, 'post_url', f)
    trytoprint(r, 'timestamp', f)
    trytoprint(r, 'date', f)
    trytoprint(r, 'note_count', f)  
    trytoprint(r, 'type', f)
    trytoprint(r, 'slug', f)
    trytoprint(r, 'tags', f)
    f.write('\n')

    f.close()
    

### MAIN FUNCTION

try:
    tagarg = sys.argv[1] 
    numposts = int(sys.argv[2])
    threshold = int(sys.argv[3])

    outfile = tagarg + '_stats.csv'

    postfile = tagarg + '_posts.csv'

    f = open(postfile, 'w')
    f.write('id, blog, url, timestamp, date, notes, type, slug, tags\n')
    f.close()

except:
    sys.exit('usage: get_tagstats.py <tagname> <numposts> <popularity threshold> [--debug]')


try: 
    sys.argv[4]
    debug = 1
except:
    debug = 0
    

client = pytumblr.TumblrRestClient(
    'KS42dOM6IqjWlNJFGTSeyrtoZUcz88UWAUBZ65zB2cy0BxYY51',
    'g6GIL8USRPZfgnScVgomGUAmbUxkNww01LU08mllATlR3111SF',
    '<oauth_token>',
    '<oauth_secret>',
)

timestamps = []
result = client.tagged(tagarg, limit=20)

# count up types and tags
typecount = {}
tagcount = {}
datecount = {}
hourcount = {}

for i in range(0, numposts/20):
    print("posts fetched: " + str(20 * i - 20))
#    sys.stderr.write(str(i))
    sys.stderr.write("\n")
    localtimestamps = []
    try:
        num = 0
        for r in result:
            num+= 1

            # timestamps
            try:
                ts = r['timestamp']
                timestamps.append(ts)
                localtimestamps.append(ts)
                d = datetime.date.fromtimestamp(ts)
                dt = datetime.datetime.fromtimestamp(ts)
                hour = dt.hour
                if debug:
                    print(d, "\n")
#                    if ts == 1320565860:
#                        print r
                
                addtocount(d, datecount)
                addtocount(hour, hourcount)
            except:
                print('failed to handle timestamp/date/hour count')

            #if debug:
             #   print timestamps , "\n"

            # types and tags
            try:
                ty = r['type']
                addtocount(ty, typecount)
            except:
                print('failed to handle type count')

            try:
                tags = r['tags']
            #        print tags
                for tag in tags:
                    tag = tag.lower()
#                    tag = re.sub(' ', '', tag)
                    addtocount(tag, tagcount)
            except:
                print('failed to handle tag count')

            # if postfile then print post
            if postfile: 
                printpost(r, postfile)
    except:
        print("bad result: ", num)
        break

    # find the earliest timestamp -- but for some reason sometimes
    # there are a few anomalous very early posts returned, so try to
    # cluster and ignore anomalously early ones.  

    # for now we'll do this with the relatively simple method of
    # popping the last timestamp off the stack and trying again any
    # time that the maximum difference in timestamps is way outside
    # the bounds of the average difference in timestamps. discard the
    # outliers.  (the outliers are still in the collected data written
    # to file, but we throw them out of the timestamps array that we
    # use to keep track of posts so far and fetch more posts.)

    # ADDENDUM AFTER THIS TURNS OUT TO HAVE ISSUES: I think sometimes
    # this is detecting that fandoms legit wax and wane, and there are
    # sometimes actual real big gaps.  New hypothesis: True big gaps
    # (not just outliers) should come in clumps.  So the biggest
    # outlier should be an outlier among the current set of 20 posts
    # AS WELL AS among the overall set of posts.

    timestamps = sorted(timestamps)
    localtimestamps = sorted(localtimestamps)
    maxdiff = 1
    avgdiff = 0
    lmaxdiff = 1
    lavgdiff = 0
    THRESHOLD = 100
    # find the max difference between two adjacent posts' timestamps
    # and the median difference between two adjacent posts' timestamps
    # if the max difference between neighbors is more than 100x the
    # median, then throw out the oldest post and repeat until that's
    # no longer the case (remove the gap)
    while ((maxdiff > THRESHOLD * avgdiff) and (lmaxdiff > THRESHOLD * lavgdiff)):
        if debug:
            print("maxdiff: ", maxdiff, ", avgdiff: ", avgdiff)
            print("lmaxdiff: ", lmaxdiff, ", lavgdiff: ", lavgdiff)

        ts1 = timestamps[:-1]
        ts2 = timestamps[1:]
        lts1 = localtimestamps[:-1]
        lts2 = localtimestamps[1:]


        tsdiff = list(map(operator.sub, ts2, ts1))
        sorteddiff = sorted(tsdiff)
        maxdiff = max(tsdiff)

        ltsdiff = list(map(operator.sub, lts2, lts1))
        lsorteddiff = sorted(ltsdiff)
        lmaxdiff = max(ltsdiff)

        # the median diff, or avgdiff, is in the middle of the sorteddiff list
        midlist = int(len(sorteddiff)/2)
        lmidlist = int(len(lsorteddiff)/2)
#        if debug:
#            print "maxdiff: "
#            print maxdiff, "\n"
#            print "midlist: "
#            print midlist, "\n"
#            print "tsdiff: "
#            print tsdiff, "\n"
#            print "sorteddiff: "
#            print sorteddiff, "\n"

        avgdiff = sorteddiff[midlist]
        lavgdiff = lsorteddiff[lmidlist]
        
#        if debug:
#            print "max timestamp difference: "
#            if maxdiff:
#                print maxdiff, "\n"
#            else:
#                print "0 \n"

        #if there is at least one outlier (at least one timestamp
        #whose difference from its neighbor is many times greater than
        #the average), then discard the earliest timestamp and try
        #again
        if (lmaxdiff > THRESHOLD * lavgdiff) and (maxdiff > THRESHOLD * avgdiff) :
            if debug:
                print("OUTLIER DETECTED!  timestamps has just had an element popped \n")
                print(datetime.date.fromtimestamp(timestamps[0]), "\n")
                print("maxdiff v avgdiff: ", maxdiff, ", ", avgdiff, "\n") 
                print("lmaxdiff v lavgdiff: ", lmaxdiff, ", ", lavgdiff, "\n") 
                print("BEFORE: ", localtimestamps, "\n")
#                print "BEFORE: ", timestamps, "\n"
            timestamps = timestamps[1:]
            localtimestamps = localtimestamps[1:]
            if debug:
                print("AFTER: ", localtimestamps, "\n")
#                print "AFTER: ", timestamps, "\n"

    earliest = timestamps[0]

#    if debug:
#        print "sorted\n"
#        print timestamps
#        print "earliest\n"
#        print earliest

    # print earliest timestamp
    sys.stderr.write(str(earliest))
    sys.stderr.write("\n")

    printall(typecount, tagcount, datecount, hourcount, threshold, outfile)

    # fetch earlier results
    result = client.tagged(tagarg, limit=20, before=earliest)
    if not result:
        break



