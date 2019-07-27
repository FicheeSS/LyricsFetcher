import mutagen as mg
from mutagen.flac import FLAC
from bs4 import BeautifulSoup
import urllib.request
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.easymp4 import EasyMP4
import glob
import sys
import multiprocessing
import re
from mutagen.easyid3 import EasyID3

SUPPORTEDFILES =(".flac",".ogg",".mp3",".m4a",".mp4")
LYRICSTAGS = ("UNSYNCEDLYRICS","LYRICS")
TOTALFILES = 0
URL_CARSET = [("ä","a"),(" ","-"),("'",""),(",",""),("/","-"),(".",""),("û","u"),("ü","u"),("ù","u"),("?","")]
JobLimit = 50

def url_contructor(artist,track):
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

def get_lyrics(artist,track):
     html = ""
     try :
          req = urllib.request.Request(url_contructor(artist,track),headers={'User-Agent' : "Magic Browser"})
          html = urllib.request.urlopen(req)
     except urllib.error.HTTPError:
          print("Lyrics not found " + str(artist) + " "+ str(track))
          return ""
     except urllib.error.URLError:
          print("Incorect URL for "+str(url_contructor(artist,track)) )
          return ""
     except UnicodeEncodeError :
          print("Non-Ascii symbol in "+ str(artist) + " "+ str(track))
          return ""
     soup = BeautifulSoup(html,features="html.parser")
     soup = soup.find("div",attrs={"class" : "lyrics"})
     soup = soup.get_text(separator=" ")
     return soup

def GetLyricsFromFile(MFile):  
     try :
          lyrics = get_lyrics(MFile["artist"],MFile["title"]) 
     except KeyError:
          try :
               lyrics = get_lyrics(MFile["Artist"],MFile["Title"])
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
#     else :
          #Nfailedfiles += 1
      

if __name__ == '__main__':
     #q = Queue.Queue("50")
     fileList = []
     ProcessFile = []
     for ext in  (SUPPORTEDFILES):
          fileList.append(glob.glob("**/*"+ext,recursive=True))
     for SFiles in SUPPORTEDFILES:
          if SFiles == ".flac":
               for y in range(len(fileList[0])):
                    ProcessFile.append(FLAC(fileList[0][y]))
                    TOTALFILES += 1
          elif SFiles == ".ogg":
               for y in range(len(fileList[1])):
                    ProcessFile.append(OggVorbis(fileList[1][y]))
                    TOTALFILES += 1
          elif SFiles == ".mp3":
               for y in range(len(fileList[2])):
                    try :
                         ProcessFile.append(EasyID3(fileList[2][y]))
                         TOTALFILES += 1     
                    except :
                         ProcessFile.append(MP3(fileList[2][y]))
                         TOTALFILES += 1
          elif SFiles == ".m4a" or SFiles == ".mp4":
               for y in range(len(fileList[3])):
                    ProcessFile.append(EasyMP4(fileList[3][y]))
                    TOTALFILES += 1
               for y in range(len(fileList[4])):
                    ProcessFile.append(EasyMP4(fileList[4][y]))
                    TOTALFILES += 1

     print(str(TOTALFILES) + " files found")
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
     jobs = []
     for i in range(len(JobsFile)) : 
          for y in range(len(JobsFile[i])):
               p = multiprocessing.Process(target=SetLyricsToFiles, args=(JobsFile[i][y],))
               jobs.append(p)
               p.start()
          for proc in jobs :
               proc.join()
          print("Batch : " + str(i+1) + " out of : " + str(len(JobsFile)))

     print("All files have been processed ")

