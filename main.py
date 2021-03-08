import mutagen as mg
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.easymp4 import EasyMP4
from mutagen.easyid3 import EasyID3 
import glob
import sys
import multiprocessing
import time
import os
from bs4 import BeautifulSoup
import urllib.request
import re
import argparse

SUPPORTEDFILES =(".flac",".ogg",".mp3",".m4a",".mp4")
LYRICSTAGS = ("UNSYNCEDLYRICS","LYRICS")
URL_CARSET = [("ä","a"),(" ","-"),("'",""),(",",""),("/","-"),(".",""),("û","u"),("ü","u"),("ù","u"),("?",""),("&","and"),(":","")]
JobLimit = 20


TOTALFILES = 0
def UrlConstructor(artist,track):
     regexparen = re.compile(".*?\((.*?)\)")
     regexcrochet = re.compile(".*?\[.*?\]")
     for delete in re.findall(regexparen, track[0]):
          track[0] = str(track[0]).replace(str(delete),"").replace("(","").replace(")","")
     for delete in re.findall(regexcrochet, track[0]):
          track[0] = str(track[0]).replace(str(delete),"").replace("[","").replace("]","")
     track[0] = str(track[0]).rstrip()
     for carset in URL_CARSET : 
          track[0] = track[0].replace(carset[0],carset[1])
          artist[0] = artist[0].replace(carset[0],carset[1])
     url = "https://genius.com/" + artist[0].lower() + "-" + track[0].lower()+ "-lyrics"
     return url

def GetLyrics(artist,track):
     html = ""
     try :
          url = UrlConstructor(artist,track)
          if not url:
               return ""
          req = urllib.request.Request(url,headers={'User-Agent' : "Magic Browser"})
          html = urllib.request.urlopen(req)
     except urllib.error.HTTPError:
          print("Lyrics not found " + str(artist) + " "+ str(track))
          return ""
     except urllib.error.URLError:
          print("Incorect URL for "+str(UrlConstructor(artist,track)) )
          return ""
     except UnicodeEncodeError :
          print("Non-Ascii symbol in "+ str(artist) + " "+ str(track))
          return ""
     try:
          soup = BeautifulSoup(html,features="html.parser").find("div",attrs={"class" : "lyrics"}).get_text(separator=" ")
     except :
          soup =""
     finally:
          return soup

def SearchMusicFiles(dir) : 
    fileList = []
    ProcessFile = []
    for ext in  (SUPPORTEDFILES):
        fileList.append(glob.glob((dir+"/**/*"+ext),recursive=True))
    for SFiles in SUPPORTEDFILES:
        if SFiles == ".flac":
            for y in range(len(fileList[0])):
                ProcessFile.append(FLAC(fileList[0][y]))
        elif SFiles == ".ogg":
            for y in range(len(fileList[1])):
                ProcessFile.append(OggVorbis(fileList[1][y]))
        elif SFiles == ".mp3":
            for y in range(len(fileList[2])):
                try :
                        ProcessFile.append(EasyID3(fileList[2][y]))  
                except :
                        ProcessFile.append(MP3(fileList[2][y]))
        elif SFiles == ".m4a" or SFiles == ".mp4":
            for y in range(len(fileList[3])):
                ProcessFile.append(EasyMP4(fileList[3][y]))
            for y in range(len(fileList[4])):
                ProcessFile.append(EasyMP4(fileList[4][y]))
    return ProcessFile

def GetLyricsFromFile(MFile):  
     
     try :
          lyrics = GetLyrics(MFile["artist"],MFile["title"]) 
     except KeyError:
          try :
               lyrics = GetLyrics(MFile["Artist"],MFile["Title"])
          except KeyError:
               print("File is lacking at least one tags ")
               return ""
          return lyrics 
     return lyrics

def SetLyricsToFiles(MFile):
     lyrics = GetLyricsFromFile(MFile)
     i = 0
     if len(lyrics) != 0: 
          for LyricsTags in LYRICSTAGS:
               try :
                    MFile[LyricsTags] = lyrics
                    MFile.save()
               except TypeError:
                    if i == len(LYRICSTAGS):
                         print("Malformed lyrics")
                         #Nfailedfiles += 1
                    else :
                         i += 1
               except KeyError :
                    try :
                         #case ID3
                         MFile["lyricist"] = lyrics 
                         MFile.save()
                    except :
                         #case MP4 only works with modified mutagen EasyMP4 library
                         try :
                              MFile["lyrics"] = lyrics
                              MFile.save()
                         except :
                              print("Please use modified Mutagen EasyMp4 library with lyrics tag")
      

if __name__ == '__main__':
     parser = argparse.ArgumentParser()
     parser.add_argument(dest='loc', metavar='d', type=str,
                         help='process file location ',required=False)
     args = parser.parse_args()
     if not args.loc or not os.path.exists(args.loc):
          print("Using current working directory")
          ProcessFile = SearchMusicFiles(os.getcwd())
     else :
          print("Using provided directory")
          ProcessFile = SearchMusicFiles(args.loc)
     #print(ProcessFile)
     startupTime = time.time()
     print(str(len(ProcessFile)) + " files found")
     #Cut the ProcessFile list into list of JobLimit size
     JobsFile = []
     for i in range(int(len(ProcessFile)/JobLimit+1)):
          JobsFile.append([])
     for i in range(int(len(ProcessFile)/JobLimit)+1):
          if (len(ProcessFile) - JobLimit * i ) > JobLimit:
               for y in range(JobLimit) :
                    JobsFile[i].append(ProcessFile[(i+1) * y])
          else :
               for y in range(len(ProcessFile) - JobLimit * i) :
                    JobsFile[i].append(ProcessFile[(i+1) * y])
     print("Starting to process files ")
     jobs = []
     for i in range(len(JobsFile)) : 
          for y in range(len(JobsFile[i])):
               p = multiprocessing.Process(target=SetLyricsToFiles, args=(JobsFile[i][y],))
               p.start()
               jobs.append(p)
          for proc in jobs :
               proc.join()
          print("Batch : " + str(i+1) + " out of : " + str(len(JobsFile)))
     
     print("Time taken : " + str(time.time() - startupTime))
     print("All files have been processed ")
     sys.exit(0)

