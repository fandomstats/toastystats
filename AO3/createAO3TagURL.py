import urllib

def TagURL(tag, type):
    tag = urllib.quote_plus(tag)
    if type == 'works':
        url = 'http://archiveofourown.org/tags/' + tag + '/works'
    else:
        url = 'http://archiveofourown.org/tags/' + tag + '/'
    return url
        
