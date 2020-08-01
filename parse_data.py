import json
import sys
import pytz
import dateutil.parser
from datetime import datetime, timedelta

shouldDownload = False

def parseArgs():
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        shouldDownload = True

# TODO: Figure out how to automate Google Takeout for the user
def downloadUserSearchHistory():
    return None

def isProductiveVideo(videoObject, channelList, keywordList):
    channel = videoObject["subtitles"][0]["name"]
    title = videoObject["title"]

    for forbiddenChannel in channelList:
        if channel == forbiddenChannel:
            return False
    
    for forbiddenKeywordInTitle in keywordList:
        if title == forbiddenKeywordInTitle:
            return False
    
    return True

def main():
    parseArgs()
    if shouldDownload:
        downloadUserSearchHistory()

    channelList = open('channels.txt').read().splitlines()
    keywordList = open('title_keywords.txt').read().splitlines()
    decodedJson = json.loads(open('watch-history.json').read())

    oneWeekBackTimestamp = pytz.UTC.localize(datetime.today() - timedelta(days=7)) # localized to UTC for comparison purposes

    isProductive = [] * len(decodedJson)
    for videoObject in decodedJson:
        dateVideoWatched = pytz.UTC.localize(dateutil.parser.parse(videoObject["time"]).replace(tzinfo=None)) # localized to UTC for comparison purposes
        if dateVideoWatched > oneWeekBackTimestamp and "subtitles" in videoObject: # if video is less than 1 week old, and if it's not an ad
            isProductive.append(isProductiveVideo(videoObject, channelList, keywordList))
    print(isProductive)

main()