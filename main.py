import mutagen as mg
from mutagen.flac import FLAC
from bs4 import BeautifulSoup
import urllib.request
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
import glob
import sys
import re
SUPPORTEDFILES =(".flac",".ogg",".mp3")
LYRICSTAGS = ("UNSYNCEDLYRICS","LYRICS")
def url_contructor(artist,track):
     # example : https://genius.com/Ariana-grande-7-rings-lyrics
     regex = re.compile(".*?\((.*?)\)")
     track[0] = re.findall(regex, track[0])
     print(track[0])
     url = "https://genius.com/" + artist[0].replace(" ","-").lower() + "-" + str(track[0]).replace(" ","-").replace("ä","a").lower() + "-lyrics"
     #print(url)
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


fileList = []
for ext in  (SUPPORTEDFILES):
     fileList.append(glob.glob("**/*"+ext,recursive=True))
#in case flac:
for y in range (len(fileList[0])):
     currentFile  = FLAC(fileList[0][y])
     lyrics = get_lyrics(currentFile["Artist"],currentFile["title"])
     if len(lyrics) != 0: 
          print("File " + str(y) +" / " + str(len(fileList[0]))+  " : " + str(int(y/len(fileList[0])*100)) + " %")
          for LyricsTags in LYRICSTAGS:
               currentFile[LyricsTags] = lyrics
          currentFile.save()
for y in range (len(fileList[1])):
     currentFile = OggVorbis(fileList[1][y])
     lyrics = get_lyrics(currentFile["Artist"],currentFile["title"])
     for LyricsTags in LYRICSTAGS:
          currentFile[LyricsTags] = lyrics
     currentFile.save()

for y in range (len(fileList[2])):
     currentFile = MP3(fileList[2][y])
     lyrics = get_lyrics(currentFile["Artist"],currentFile["title"])
     for LyricsTags in LYRICSTAGS:
          currentFile[LyricsTags] = lyrics
     currentFile.save()
