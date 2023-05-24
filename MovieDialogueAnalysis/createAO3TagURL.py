import urllib.request, urllib.parse, urllib.error
import convert

convertToAO3 = convert.convertToAO3

def TagURL(tag, type, verbose):
    tag = convertToAO3(tag, 'tag', verbose)
    tag = tag[0]
#    print tag
#    tag = urllib.quote(tag)
    if type == 'works':
        url = 'http://archiveofourown.org/tags/' + tag + '/works'
    else:
        url = 'http://archiveofourown.org/tags/' + tag + '/'
    return url
