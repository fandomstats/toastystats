README: fandom stats data for AO3 tags
Author: destinationtoast@gmail.com
Last updated: June 30, 2019

This code automates gathering aggregate statistics about AO3 overall
and specific AO3 tags (e.g.., it can't provide info about individual
fanworks, but can tell you how many there are within a fandom, how
many of those are F/F, and how that has changed over time).  It’s
somewhat brittle code and poorly documented in places, and I’m sorry
about that. :P Explanations and Usage examples below.

if you get dependency errors when trying to run these, I recommend
using pip-install or a similar python package installer.

******************************************
CASE 1: FINDING THE BIGGEST FANDOMS ON AO3
******************************************

REQUIRED TOASTY FILES:
findBigFandoms.py
findBigFandomsFiltered.py
topFandoms.py

METHOD 1: These scripts find the current largest fandoms on AO3, broken down by
the categories that AO3 divides them into.  They also output the
number of fanworks in each fandom.  For a list of all media
categories, see the headers on this page:
http://archiveofourown.org/media 

USAGE:
findBigFandoms[Filtered].py <media category> <min num fanworks>

(The "Filtered" version excludes "& Related Fandoms" and "All Media Types.")


*** Example 1a: Find TV shows on AO3 with over 50,000 fanworks:

> python findBigFandoms.py "TV Shows" 50000

*** Example 1b: Find all TV shows on AO3, excluding umbrella fandoms:

> python findBigFandomsFiltered.py "TV Shows" 0

METHOD 2: This script finds the top fandoms for all of the categories
on AO3 -- both overall and broken down by category.  It takes longer
to run than the previous scripts (but still < 20 seconds).

*** Example 2: Find top 20 fandoms on AO3 overall, and broken down by
    category (excluding umbrella fandoms; use "True" if you want to
    include them):

> python topFandoms.py 20 False

******************************************
CASE 2: GETTING SUMMARY STATS FOR AO3 TAGS
******************************************

REQUIRED TOASTY FILES:
makeSearchesForTags.py
doSearches.py
AO3search.py
importJSON.py
convert.py
UnicodeToURL.py

This code lets you gather the sidebar "Sort & Filter" info about a
bunch of fandoms or tags.

First, create a text file containing a list of all the tags (fandoms,
"Fluff", "M/M" -- whatever) that you want information about, one per
line.  Then create a list of corresponding AO3 searches, and execute
them.

USAGE:
makeSearchesForTags.py <list of tags infile> <JSON outfile>
doSearches.py <JSON infile> <CSV outfile>

*** Example:

> python makeSearchesForTags.py TopFandoms.txt TopFandoms.json

> python doSearches.py TopFandoms.json TopFandomsStats.csv


*******************************************
CASE 3: TRACKING AO3 TAG ACTIVITY OVER TIME
*******************************************

REQUIRED TOASTY FILES:
makeTagTimeSearchesFlex.py
doUnsortedSearches.py
AO3search.py
importJSON.py
convert.py
UnicodeToURL.py

This code allows you to track how a given tag or pair of tags has
changed over time on AO3. There are two scripts -- the first generates
a list of searches to perform, and the second executes them and
outputs the results.

USAGE: 
makeTagTimeSearchesFlex.py <tag1> <tag2> <timeframe> <num units> <JSON outfile name>
doUnsortedSearches.py <JSON infile name> <CSV outfile name> 

*** EXAMPLE 1: Fetch data for a monthly timeline of Harry Potter fic
with an Angst tag (for the past 12 months):

> python makeTagTimeSearchesFlex.py “Harry Potter - J. K. Rowling” “Angst” month 12 hp.json

> python doUnsortedSearches.py hp.json hp.csv

*** EXAMPLE 2: Fetch data for a daily timeline of Harry Potter fic for
    the past 100 days:

> python makeTagTimeSearchesFlex.py “Harry Potter - J. K. Rowling” “” day 100 hp.json

> python doUnsortedSearches.py hp.json hp.csv

*** EXAMPLE 3: Fetch data for a yearly timeline of fic with “Fluff” and
    “Angst” for the past 5 years:

> python makeTagTimeSearchesFlex.py “Fluff” “Angst” year 5 flangst.json

> python doUnsortedSearches.py flangst.json flangst.csv

***********************************************
CASE 4: TRACKING OVERALL AO3 ACTIVITY OVER TIME
***********************************************

REQUIRED TOASTY FILES:
(same as Case 3)

The same script as before (unintentionally!) also works to pull the total
number of fanworks posted to AO3 in a given time period.

*** EXAMPLE: Fetch data for a yearly timeline of fanworks on AO3 for
    the past 5 years:

> python makeTagTimeSearchesFlex.py “” “” year 5 ao3.json

> python doUnsortedSearches.py ao3.json ao3.csv

********************************************
CASE 5: FIND TOP SHIPS AND FANDOMS FOR A TAG 
********************************************

REQUIRED TOASTY FILES:
toastyTools.py
topShipsAndFandoms.py
getTopShipsAndFandomsLibrary.py
AO3search.py
convert.py

The goal here is to find the biggest ships and fandoms for any given
tag -- e.g., what are the biggest femslash ships and fandoms, or which
ships have the most AUs -- and to dig far past the top 10 that are
easy to find. 

*** EXAMPLE: Find the ships and fandoms that most often co-occur with
    the "F/F" tag.  

> python topShipsAndFandoms.py "F/F" includeTags.txt excludeTags.txt 
  100 shipOutfile.csv fandomOutfile.csv shipDiscards.csv fandomDiscards.csv

includeTags and excludeTags: Extra tags that should also be included
or excluded in the search can be listed -- one per line -- in the
specified files. For instance, you can list F/M and M/M in the
excludeTags.txt file to weed out F/F fanworks where the F/F might be a
secondary ship.  These files may be left empty.

The number (100 in the example) is the minimum ship size you're
interested in finding. This algorithm doesn't guarantee that all ships
near the threshold will be returned, but most ships over the threshold
should be.

I've added shipDiscards and fandomDiscards outfiles because it can be
very useful to look at which other ships and fandoms were evaluated
but failed to meet the criteria.

NOTE: I recently realized that many fandoms were accidentally going
missing, and I rewrote this function in an attempt to fix the error.
It now does a depth-first search through fandoms (don't worry if that
doesn't make sense), and potentially takes much longer to do its
search.  But I believe it returns a better set of results. However, I
have not finished verifying that it now returns a complete list of
ships and fandoms that meet the criteria, so still be aware that some
may be missing.

********************************************
CASE 6: FIND FEMSLASH DATA FOR A SET OF TAGS
********************************************

REQUIRED TOASTY FILES:
getFemslashInfo.py
toastyTools.py
AO3search.py
convert.py

This function takes in a list of tags from a file, and for each tag,
finds a bunch of relevant info for femslash stats -- how many works
does the tag have?  How many F/F works? How many exclusive F/F works
(F/F works after excluding F/M and M/M)?  How many exclusive F/F works
within a given time frame?  It outputs the results to CSV.

*** EXAMPLE: Get femslash stats that include number of exclusive F/F works in 2020:

> python getFemslashInfo.py fftags.txt outfile.csv "2020-01-01" "2020-12-31"


**************************************************
CASE 7: GET DATA ABOUT TAGS FROM A PARTICULAR TIME
**************************************************

REQUIRED FILES:
getTagLimitedTimeData.py
toastyTools.py
AO3search.py
convert.py

This function takes in a list of tags from a file, and for each tag,
finds out how many works were produced between a start date and end
date specified by the user.

*** EXAMPLE: For every tag in tags.txt, find how many works were produced during the year 2020

> python getTagLimitedTimeData.py tags.txt "2020-01-01" "2020-12-31" out.csv

*******************************************************
CASE 7: GET DATA ABOUT LANGUAGES FROM A PARTICULAR TIME
*******************************************************

REQUIRED FILES:
getLanguageLimitedTimeData.py
toastyTools.py

This function takes in a list of language codes (e.g., "en" for
English; "es" for Spanish) from a file, and for each language, finds
out how many works were produced during a specific time frame
specified by the user.  The timeframe is specified in the same way
that AO3 Works Search specifies time frames.  (Sorry this is
inconsistent with how tag time frames work, above; I may fix this
later.)  The user can also decide whether to only include single
chapter works (penultimate argument is set to True) or to count all
works (penultimate argument is set to False).

*** EXAMPLE: For every language whose language code is listed in
    languages.txt, find how many single chapter works were produced in
    the last 19 days

> python getLanguageLimitedTimeData.py languageCodes.txt "< 20 days" True out.csv