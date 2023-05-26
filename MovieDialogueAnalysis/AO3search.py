import sys
import convert
import re
from bs4 import BeautifulSoup
import urllib3
import pdb
import UnicodeToURL

DEBUG=0

class AO3data:
    # ********* DATA FIELDS
    searchParams = {}
    numworks = -1
    tagID = -1
    popularity = {"kudos": -1, "hits": -1, "comments": -1, "bookmarks": -1}
    categories = {"rating": {"num": 5, "top": {}}, "warning": {"num": 6, "top": {}}, "category": {"num": 6, "top": {}}, "fandom": {"num": 10, "top": {}}, "character": {"num": 10, "top": {}}, "relationship": {"num": 10, "top": {}}, "freeform": {"num": 10, "top": {}}}
    htmlData = {}

    # ********* METHODS

    # METHOD: printAll
    def printAll(self):
        print(self.searchParams, ", ", self.numworks)
        print(self.categories)
    
    # METHOD: printCSV
    def printCSV(self, fo):
        for k in list(self.searchParams.keys()):
            string = self.searchParams[k] + ", "
            fo.write(string)
        try:
            fo.write(str(self.numworks))
        except:
            pdb.set_trace()
            print("COULDN'T WRITE TO FILE: ", self.numworks)
        fo.write(", ")

        sortedcats = sorted(self.categories.keys())
        for cat in sortedcats:
            num = self.categories[cat]["num"]
            currlist = self.categories[cat]["top"]
            sortedkeys = sorted(currlist, key=currlist.get, reverse=True)
            count = 0
            for k in sortedkeys: 
                fo.write(k + ", ")
#                print k.encode("utf-8") + ", "
                fo.write(str(currlist[k]) + ", ")
#                print str(currlist[k]) + ", "
                count = count + 1
            for i in range(count, num):
                fo.write(", , ")
#                print ", , "
                
        #NEWLINE
        fo.write("\n")

    # METHOD: printShortCSV
        # just the NumWorks
    def printShortCSV(self, fo):
        for k in list(self.searchParams.keys()):
            string = self.searchParams[k] + ", "
            fo.write(string)
        try:
            fo.write(str(self.numworks))
            fo.write("\n")
        except:
            pdb.set_trace()
            print("COULDN'T WRITE TO FILE: ", self.numworks)
            


    # METHOD: printShortCSVHeaders
    def printShortCSVHeaders(self, fo):
        for k in list(self.searchParams.keys()):
            string = k + ", "
            fo.write(string)
        fo.write("Num Works,")

        #NEWLINE
        fo.write("\n")

    # METHOD: printCSVHeaders
    def printCSVHeaders(self, fo):
        for k in list(self.searchParams.keys()):
            string = k + ", "
            fo.write(string)
        fo.write("Num Works,")

        # PRINT TOP X names
        for cat in sorted(self.categories.keys()):
            val = self.categories[cat]["num"]
            for i in range(0, val):
                tmp = "Top " + cat + " " + str(i) + ", "
                fo.write(tmp)
                fo.write("count, ")
 
        #NEWLINE
        fo.write("\n")
    
    # METHOD: fetchHTML
    def fetchHTML(self):
        if self.htmlData == {}:            
            http = urllib3.PoolManager()
            r = {}
            if DEBUG:
                print(self.searchURL)
            try:
                r = http.request('GET', self.searchURL)
#                print "made it"
                soup = BeautifulSoup(r.data, 'html.parser')
                soup.prettify()                
                self.htmlData = soup
                return soup
            except:
                print("ERROR: failure to fetch URL: ", self.searchURL)
        else:
            return self.htmlData
                                

    # METHOD: getNumWorks
    # the second parameter indicates if this is a Sort and Filter type search or the other kind of search
    def getNumWorks(self, isSorted):
        if self.searchURL == '':
            sys.exit("empty searchURL field!")

        
        # extract the number of works returned by this search
        soup = self.fetchHTML()
        try:
            if isSorted:
                tag = soup.find_all(text=re.compile("Work(s)*( found)* in"))
            else:
                tag = soup.find_all(text=re.compile("[0-9]+ Found"))

#            print tag
                
        except AttributeError:
            print("ERROR: empty HTML data: ", self.searchURL)
            self.numworks = -2
            return
            
        try:
            line =  tag[0]
#            print line
        except:
            line = ''
            self.numworks = -2
#            sys.exit("no number of works found")

        nums = re.findall('([0-9]+)', line)
        if len(nums) == 0:
            self.numworks = -2
#            sys.exit("No numbers found in H2 tag content")
        elif len(nums) == 1:
            self.numworks = int(nums[0])
        else: 
            self.numworks = int(nums[2])

#        print "Num works found: ", self.numworks

        if DEBUG:
            print(self.numworks)
        return self.numworks


    # METHOD: getTopInfo -- scrape the top 10 ratings, etc from sidebar
    def getTopInfo(self):

        for k in list(self.categories.keys()):
            self.categories[k]["top"] = {}

        if self.searchURL == '':
            sys.exit("empty searchURL field!")

        soup = self.fetchHTML()

        # look up tag ID
        try:
            # the tag ID is contained in the RSS feed link
            rss = soup.findAll('a','rss')[0]
            #print "~~~~~***",rss['href']
            m = re.search('[0-9]+', rss['href'])
            #print m.group(0)
            self.tagID = int(m.group(0))
        except:
            print("ERROR: couldn't find tagID")


        for k in list(self.categories.keys()):
            idstring = "tag_category_" + k

            try:
                topList = soup.findAll("dd", {"id" : idstring})
            except AttributeError:
                print("ERROR: empty HTML data: ", self.searchURL)
                self.numworks = -2
                return
            
            try:
                top = topList[0]
            except:
                print("ERROR! " + k)  
                return
            
            labels = top.find_all("label")
            for L in labels:
                tmp = re.compile('(.*) \(([0-9]+)\)')
                m = tmp.match(L.text)
                self.categories[k]["top"][m.group(1)] = int(m.group(2))




    # METHOD: createSearchURL
    def createSearchURL(self):
        if self.searchParams == {}:
            print("ERROR: empty searchParams field!")

        # fetch the date
        d = ''
        try:
            d = self.searchParams['date']
            tmp = convert.convertToAO3(d, 'within', False)
            d = tmp[0]
        except:
            dummy = ''

        # fetch the category(ies)
        c = ''        
        try:
            c = self.searchParams['category']
            tmp = convert.convertToAO3(c, 'cat', False)
            c = tmp[0]
        except:
            dummy = ''
            #print "no category in searchParams: ", self.searchParams
        
        # fetch the warning(s)
        w = ''        
        try:
            w = self.searchParams['warning']
            tmp = convert.convertToAO3(w, 'warn', False)
            w = tmp[0]
        except:
            dummy = ''
            #print "no warning in searchParams ", self.searchParams
            
        # fetch the tag(s)
        t = str('&tag_id=')
        try:
            tag = self.searchParams['tag']
            tmp = convert.convertToAO3(tag, 'tag', False)    
            t += str(tmp[0])
        except:
            dummy = ''
            #print "no tag in searchParams ", self.searchParams

        # fetch the "search within results"
        swr = '&work_search%5Bquery%5D='
        try:
            within = self.searchresults['search within results']
            tmp = convert.convertToAO3(within, 'within', False)    
            swr += tmp[0]
        except:
            dummy = ''
            #print "no search within results in searchParams ", self.searchParams

        # assemble the URL
        urlprefix = 'http://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at'
        urlprequery = '&work_search%5Bother_tag_names%5D='
        urlpredate = '&work_search%5Brevised_at%5D='
        urlpretag = '&work_search%5Blanguage_id%5D=&work_search%5Bcomplete%5D=0'
        
        tmp = str(urlprefix + c + w + urlpredate + d + urlprequery + swr + urlpretag + t)
        self.searchURL = tmp
        
        
    # METHOD: createUnsortedSearchURL
    # this will only be useful for doing a getNumWorks call; does not include all the top X info
    # in the Sort & Filter sidebar
    # but it's better (?) for searching time slices and multiple tags 
    def createUnsortedSearchURL(self):
        if self.searchParams == {}:
            print("ERROR: empty searchParams field!")

        # fetch the date
        d = ''
        try:
            d = self.searchParams['date']
            tmp = convert.convertToAO3(d, 'unsorted', False)
            d = tmp[0]
        except:
            dummy = ''

        # fetch the fandom(s)
        fan = ''
        try:
            fan = self.searchParams['fandom']
            tmp = convert.convertToAO3(fan, 'unsorted', False)    
            fan = tmp[0]
            # also replace the original version of the fandom tag with the new version
            # to remove any commas in the CSV outfile
            self.searchParams['fandom'] = fan
        except:
            dummy = ''

        # fetch the freeform tag(s)
        free = ''
        try:
            free = self.searchParams['freeform']
            tmp = convert.convertToAO3(free, 'unsorted', False)    
            free = tmp[0]
            # also replace the original version of the freeform tag with the new version
            # to remove any commas in the CSV outfile
            self.searchParams['freeform'] = free
        except:
            dummy = ''

        print(d)
        print(fan)
        print(free)
        # assemble the URL
        urlpredate = 'http://archiveofourown.org/works/search?utf8=%E2%9C%93&work_search%5Bquery%5D=&work_search%5Btitle%5D=&work_search%5Bcreator%5D=&work_search%5Brevised_at%5D='
        urlprefandom = '&work_search%5Bcomplete%5D=0&work_search%5Bsingle_chapter%5D=0&work_search%5Bword_count%5D=&work_search%5Blanguage_id%5D=&work_search%5Bfandom_names%5D='
        urlprefreeform = '&work_search%5Brating_ids%5D=&work_search%5Bcharacter_names%5D=&work_search%5Brelationship_names%5D=&work_search%5Bfreeform_names%5D='
        urlsuffix = '&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=&work_search%5Bsort_direction%5D=&commit=Search'
        
        tmp = str(urlpredate + d + urlprefandom + fan + urlprefreeform + free + urlsuffix)
        self.searchURL = tmp
        
        


#" " " 
#notes on goals:
#Sample searches:
#* all fandoms: proportion of femslash
#* all fandoms: median number of kudos
#* all fandoms: mean word count
#* the number of fics with each pairing in a given fandom
#* all fandoms: ratio of Gen to Shipping
#* subset of fandoms: " " 
#* activity over time in a given fandom (vs. in AO3)


#STRUCTURE:
#* search parameters
#* data to collect
#-- number of works
#-- median number of kudos/comments/bookmarks/hits
#* method: print all in CSV format
#* method: print headers in CSV format
#* method: fetch number of works
#* method: fetch median number of X
#" " " 
