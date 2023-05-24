import urllib.request, urllib.parse, urllib.error
import convert

convertToAO3 = convert.convertToAO3

def FandomSearchURL(fandom, verbose):
        
    # assemble the URL                                                      

    urlprefix = "http://archiveofourown.org/works/search?utf8=%E2%9C%93&work_search%5Bquery%5D=&work_search%5Btitle%5D=&work_search%5Bcreator%5D=&work_search%5Brevised_at%5D=&work_search%5Bcomplete%5D=0&work_search%5Bsingle_chapter%5D=0&work_search%5Bword_count%5D=&work_search%5Blanguage_id%5D=&work_search%5Bfandom_names%5D="
    urlsuffix = "&work_search%5Brating_ids%5D=&work_search%5Bcharacter_names%5D=&work_search%5Brelationship_names%5D=&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=&work_search%5Bsort_direction%5D=&commit=Search"
    fandom = convertToAO3(fandom, 'unsorted', verbose)
    fandom = fandom[0]
    searchURL = str(urlprefix + fandom + urlsuffix)
    if verbose:
        print(searchURL)

    return searchURL

def CombinedSearchURL(fandom, characterID, verbose):
    urlprefix = 'http://archiveofourown.org/works?utf8=%E2%9C%93&commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&work_search%5Bcharacter_ids%5D%5B%5D='
    urlmidfix = '&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&work_search%5Bcomplete%5D=0&tag_id='

    fandom = convertToAO3(fandom, 'tag', verbose)
    fandom = fandom[0]
    searchURL = str(urlprefix + str(characterID) + urlmidfix + fandom)
    if verbose:
        print(searchURL)

    return searchURL
