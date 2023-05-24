import re
import urllib.request, urllib.parse, urllib.error

def convertToAO3(s, sType, verbose):
    
    # handle unsorted search conversions
    if sType == 'unsorted':
        if verbose:
            print('converting tag: ', s)
        tmp = s
#        s = re.sub(' ', '+', s)
#        s = re.sub('\/', '%2F', s)
#        s = re.sub('\,', '%2C', s)
#        s = re.sub('\|', '%7C', s)
#        s = re.sub('\(', '%28', s)
#        s = re.sub('\)', '%29', s)
#        s = re.sub('\&', '%26', s)
        s = urllib.parse.quote_plus(s)
        return [s, tmp] 
#        return [s.encode('utf-8'), tmp] 

    # handle tag
    if sType == 'tag':
        if verbose:
            print('converting tag: ', s)
        tmp = s
#        s = re.sub(' ', '+', s)
#        s = re.sub('\ ', '%20', s)
        s = re.sub('\.', '*d*', s)
        s = re.sub('\?', '*q*', s)
        s = re.sub('\/', '*s*', s)
#        s = re.sub('\,', '%2C', s)
#        s = re.sub('\|', '%7C', s)
#        s = re.sub('\(', '%28', s)
#        s = re.sub('\)', '%29', s)
#        s = re.sub('\&', '%26', s)
        s = urllib.parse.quote(s)
        return [s, tmp] 
#        return [s.encode('utf-8'), tmp] 

    # handle search within results
    if sType == 'within':
        if verbose:
            print('converting within: ', s)
        tmp = s
#        s = re.sub(' ', '+', s)
#        s = re.sub('\/', '%2F', s)
#        s = '&work_search%5Bquery%5D=' + s
        s = urllib.parse.quote(s)
        return [s, tmp] 
#        return [s.encode('utf-8'), tmp] 

    # handle categories
    elif sType == 'cat':
        if verbose:
            print('converting cat: ', s, ', type: ', type(s))
        c = ''
        tmp = ''

        # convert s to a list
        if isinstance(s, str) or isinstance(s, str):
            s = [s]
            if verbose:
                print('converting string to list: ', s)
        
        s = sorted(s)

        # for each category, append appropriate URL string 
        for cat in s:
            tmp += cat
            tmp += ' '
            if verbose:
                print('cat:', cat)
            if cat.lower() == 'm/m':
                if verbose:
                    print('cat = M/M!')
                c += '&work_search%5Bcategory_ids%5D%5B%5D=23'
            elif cat.lower() == 'f/m':
                if verbose:
                    print('cat = F/M!')
                c += '&work_search%5Bcategory_ids%5D%5B%5D=22'
            elif cat.lower() == 'f/f':
                if verbose:
                    print('cat = F/F!')
                c += '&work_search%5Bcategory_ids%5D%5B%5D=116'
            elif cat.lower() == 'gen':
                if verbose:
                    print('cat = Gen!')
                c += '&work_search%5Bcategory_ids%5D%5B%5D=21'
            elif cat.lower() == 'other':
                if verbose:
                    print('cat = Other!')
                c += '&work_search%5Bcategory_ids%5D%5B%5D=24'
            elif cat.lower() == 'multi':
                if verbose:
                    print('cat = Multi!')
                c += '&work_search%5Bcategory_ids%5D%5B%5D=2246'
            else:
                c = 'xxxxxx'
                if verbose:
                    print('unrecognized category!')

        return [c, tmp]

    # handle warnings
    elif sType == 'warn':
        if verbose:
            print('converting warn: ', s, ', type: ', type(s))
        w = ''
        tmp = ''

        # convert s to a list
        if isinstance(s, str) or isinstance(s, str):
            s = [s]
            if verbose:
                print('converting string to list: ', s)
        
        s = sorted(s)

        # for each warning, append appropriate URL string 
        for warn in s:
            tmp += warn
            tmp += ' '
            if verbose:
                print('warn:', warn)
            if warn.lower() == 'no':
                if verbose:
                    print('warn = no')
                w += '&work_search%5Bwarning_ids%5D%5B%5D=16'
            elif warn.lower() == 'choose':
                if verbose:
                    print('warn = choose')
                w += '&work_search%5Bwarning_ids%5D%5B%5D=14'
            elif warn.lower() == 'violence':
                if verbose:
                    print('warn = violence')
                w += '&work_search%5Bwarning_ids%5D%5B%5D=17'
            elif warn.lower() == 'death':
                if verbose:
                    print('warn = death')
                w += '&work_search%5Bwarning_ids%5D%5B%5D=18'
            elif warn.lower() == 'rape':
                if verbose:
                    print('warn = rape')
                w += '&work_search%5Bwarning_ids%5D%5B%5D=19'
            elif warn.lower() == 'underage':
                if verbose:
                    print('warn = underage')
                w += '&work_search%5Bwarning_ids%5D%5B%5D=20'
            else:
                w = 'xxxxxx'
                if verbose:
                    print('unrecognized warning!')

        return [w, tmp]


    else:
        sys.exit('unrecognized type!')


#def convertFromAO3(s, verbose):
    
#        s = re.sub('\&amp\;', '&', s)
#        s = re.sub('\%22', '"', s)
