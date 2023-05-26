#import urllib.parse, urllib.request, urllib.parse, urllib.error

#def fixurl(url):
    # turn string into unicode
#    if not isinstance(url,str):
#        url = url.decode('utf8')

    # parse it
#    parsed = urllib.parse.urlsplit(url)

    # divide the netloc further
#    userpass,at,hostport = parsed.netloc.rpartition('@')
#    user,colon1,pass_ = userpass.partition(':')
#    host,colon2,port = hostport.partition(':')

    # encode each component
    #scheme = parsed.scheme.encode('utf8')
    #user = urllib.parse.quote(user.encode('utf8'))
    #colon1 = colon1.encode('utf8')
    #pass_ = urllib.parse.quote(pass_.encode('utf8'))
    #at = at.encode('utf8')
    #host = host.encode('idna')
    #colon2 = colon2.encode('utf8')
    #port = port.encode('utf8')
    #path = '/'.join(  # could be encoded slashes!
    #   urllib.parse.quote(urllib.parse.unquote(pce).encode('utf8'),'')
    #   for pce in parsed.path.split('/')
    #)
    #query = urllib.parse.quote(urllib.parse.unquote(parsed.query).encode('utf8'),'=&?/')
    #fragment = urllib.parse.quote(urllib.parse.unquote(parsed.fragment).encode('utf8'))

    # put it back together
#    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
#    return urllib.parse.urlunsplit((scheme,netloc,path,query,fragment))

