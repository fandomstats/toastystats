import sys
from toastyTools import getArguments, getListFromTextFile, prepCSVOutfile, getAO3LanguageTimeframeURL,getNumWorksFromURL, writeFieldToCSV, writeEndlineToCSV

DEBUG=1

infile, timeframe, singleChapter, outfile = getArguments(sys.argv, 4, 'Usage: getLanguageLimitedTimeData.py languageCodeFile timeframe singleChapter outfile (e.g., getLanguageLimitedData.py languageCodeList.txt "< 20 days" True out.csv');

langs = getListFromTextFile(infile)
outfp = prepCSVOutfile(outfile, "language,works "+timeframe)

for langCode in langs:
    if DEBUG:
        print(langCode)

    # write to CSV: language code
    writeFieldToCSV(outfp, langCode)

    # get data on how many works exist for this language code overall and within limited timeframe, and write to CSV
    limitedURL = getAO3LanguageTimeframeURL(langCode,timeframe,singleChapter)
    if DEBUG:
        print(limitedURL)

    limitedWorks = getNumWorksFromURL(limitedURL, False)
    if DEBUG:
        print(limitedWorks)

    writeFieldToCSV(outfp, str(limitedWorks))

    # end the CSV line
    writeEndlineToCSV(outfp)
