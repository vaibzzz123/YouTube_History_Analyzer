
import os
import isodate
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

def convert(seconds): 
  seconds = seconds % (24 * 3600) 
  hours = seconds // 3600
  seconds %= 3600
  minutes = seconds // 60
  seconds %= 60
  return hours, minutes, seconds

def parseTimestampForTime(timestamp):
  timestampParsed = isodate.parse_duration(timestamp) # parsed as datetime.timedelta in seconds, need to convert to H, M, and S
  hours, minutes, seconds = convert(timestampParsed.seconds)
  return hours, minutes, seconds

def getVideoInformationFromId(id):
  youtube = build('youtube', 'v3', developerKey=os.getenv("API_KEY"))
  result = youtube.videos().list(id=id, part="contentDetails").execute()
  timeISOEncoded = result["items"][0]["contentDetails"]["duration"]
  hours, minutes, seconds = parseTimestampForTime(timeISOEncoded)
  return hours, minutes, seconds

