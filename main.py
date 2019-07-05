import mutagen as mg
from mutagen.flac import FLAC
from bs4 import BeautifulSoup
import urllib.request
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
import glob
import sys
import re
from mutagen.easyid3 import EasyID3
import mutagen
SUPPORTEDFILES =(".flac",".ogg",".mp3",".m4a",".mp4")
LYRICSTAGS = ("UNSYNCEDLYRICS","LYRICS")
Nfailedfiles = 0
TOTALFILES = 0


def url_contructor(artist,track):
     # example : https://genius.com/Ariana-grande-7-rings-lyrics
     regexparen = re.compile(".*?\((.*?)\)")
     regexcrochet = re.compile(".*?\[.*?\]")
     for delete in re.findall(regexparen, track[0]):
          track[0] = str(track[0]).replace(str(delete),"").replace("(","").replace(")","")
     for delete in re.findall(regexcrochet, track[0]):
          track[0] = str(track[0]).replace(str(delete),"").replace("[","").replace("]","")
     track[0] = str(track[0]).rstrip()
     url = "https://genius.com/" + artist[0].replace(" ","-").lower() + "-" + str(track[0]).replace(" ","-").replace("ä","a").replace("'","").replace(",","").replace("/","-").replace(".","").lower()+ "-lyrics"
     return url

def get_lyrics(artist,track):
     html = ""
     try :
          req = urllib.request.Request(url_contructor(artist,track),headers={'User-Agent' : "Magic Browser"})
          html = urllib.request.urlopen(req)
     except urllib.error.HTTPError:
          print("Lyrics not find " + str(artist) + " "+ str(track))
          return ""
     except urllib.error.URLError:
          print("Incorect URL for "+str(url_contructor(artist,track)) )
          return ""
     except UnicodeEncodeError :
          print("Non-Ascii symbol in "+ str(artist) + " "+ str(track))
          return ""
     soup = BeautifulSoup(html,features="html.parser")
     #print(soup.prettify())
     soup = soup.find("div",attrs={"class" : "lyrics"})
     soup = soup.get_text(separator=" ")
     #print(soup)
     return soup
def GetLyrics(MFile):  
     try :
          lyrics = get_lyrics(MFile["Artist"],MFile["title"]) 
     except KeyError:
          try :
               lyrics = get_lyrics(MFile["Artist"],MFile["Title"])
          except KeyError:
               print("File is lacking at least one tags ")
               return ""
          return lyrics
     return lyrics


fileList = []
ProcessFile = []
for ext in  (SUPPORTEDFILES):
     fileList.append(glob.glob("**/*"+ext,recursive=True))
#in case flac:
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
               ProcessFile.append(MP4(fileList[3][y]))
               TOTALFILES += 1
          for y in range(len(fileList[4])):
               ProcessFile.append(MP4(fileList[4][y]))
               TOTALFILES += 1 

print(str(TOTALFILES) + " files found")

for MFile in ProcessFile:
     lyrics = GetLyrics(MFile) 
     i = 0
     if len(lyrics) != 0: 
          print("File " + str(ProcessFile.index(MFile)) +" / " + str(len(ProcessFile))+  " : " + str(int(ProcessFile.index(MFile)/len(ProcessFile)*100)) + " %")
          for LyricsTags in LYRICSTAGS:
               try :
                    MFile[LyricsTags] = lyrics
                    MFile.save()
               except TypeError:
                    if i == len(LYRICSTAGS):
                         print("Malformed lyrics")
                    else :
                         i += 1
               except EasyID3KeyError :
                    MFile["LYR"] = lyrics
                    MFile.save()

     else :
          Nfailedfiles += 1

print("All files have been processed ")
print("Lyrics found : "+str(TOTALFILES-Nfailedfiles) + ". Lyrics not found or instrumental : " +str(Nfailedfiles) )

