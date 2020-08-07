import json
import sys
import os
import pytz
import dateutil.parser
from datetime import datetime, timedelta
from yt_api import getVideoInformationFromId, convert

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

def writeVideoInformationToFile(videoInformation):
    jsonStr = json.dumps(videoInformation, indent=2)
    parsedDataJsonFile = open('parsed_data.json', "w")
    parsedDataJsonFile.write(jsonStr)

def printStatisticsOnAllData(videoInformation):
    totalHours = 0
    totalMinutes = 0
    totalSeconds = 0

    unproductiveHours = 0
    unproductiveMinutes = 0
    unproductiveSeconds = 0
    for video in videoInformation:
        if video["isProductive"] == False:
            unproductiveHours += video["hours"]
            unproductiveMinutes += video["minutes"]
            unproductiveSeconds += video["seconds"]
        totalHours += video["hours"]
        totalMinutes += video["minutes"]
        totalSeconds += video["seconds"]
    
    totalOverallInSeconds = (totalHours * 60 * 60) + (totalMinutes * 60) + totalSeconds
    totalUnproductiveInSeconds = (unproductiveHours * 60 * 60) + (unproductiveMinutes * 60) + unproductiveSeconds
    
    percentageUnproductive = (float(totalUnproductiveInSeconds)/float(totalOverallInSeconds)) * 100

    finalOverallHours, finalOverallMinutes, finalOverallSeconds = convert(totalOverallInSeconds)
    finalUnproductiveHours, finalUnproductiveMinutes, finalUnproductiveSeconds = convert(totalUnproductiveInSeconds)

    finalString = f'Unproductive time: {finalUnproductiveHours}h{finalUnproductiveMinutes}m{finalUnproductiveSeconds}s\n'
    finalString += f'Total time: {finalOverallHours}h{finalOverallMinutes}m{finalOverallSeconds}s\n'
    finalString += f'Percentage of time unproductive: {percentageUnproductive:0.2f}%\n'

    print(finalString)

def main():
    parseArgs()
    if shouldDownload:
        downloadUserSearchHistory()

    channelList = open('channels.txt').read().splitlines()
    keywordList = open('title_keywords.txt').read().splitlines()
    decodedJson = json.loads(open('watch-history.json').read())

    oneWeekBackTimestamp = pytz.UTC.localize(datetime.today() - timedelta(days=7)) # localized to UTC for comparison purposes

    videoInformation = []
    if not os.path.isfile('parsed_data.json'):
        for videoObject in decodedJson:
            dateVideoWatched = pytz.UTC.localize(dateutil.parser.parse(videoObject["time"]).replace(tzinfo=None)) # localized to UTC for comparison purposes
            if dateVideoWatched > oneWeekBackTimestamp and "subtitles" in videoObject: # if video is less than 1 week old, and if it's not an ad
                isProductive = isProductiveVideo(videoObject, channelList, keywordList)
                videoUrl = videoObject["titleUrl"]
                videoId = videoUrl.split("?v=")[1]
                hours, minutes, seconds = getVideoInformationFromId(videoId)
                videoData = dict([
                    ("videoTitle", videoObject["title"]),
                    ("videoId", videoId),
                    ("isProductive", isProductive),
                    ("hours", hours),
                    ("minutes", minutes),
                    ("seconds", seconds),
                ])
                videoInformation.append(videoData)
        writeVideoInformationToFile(videoInformation)
    else:
        videoInformation=json.loads(open('parsed_data.json').read())
    printStatisticsOnAllData(videoInformation)

    # print(videoInformation)

main()