import urllib.request, urllib.parse, urllib.error

def TagURL(tag, type):
    tag = urllib.parse.quote_plus(tag)
    if type == 'works':
        url = 'http://archiveofourown.org/tags/' + tag + '/works'
    else:
        url = 'http://archiveofourown.org/tags/' + tag + '/'
    return url
        
