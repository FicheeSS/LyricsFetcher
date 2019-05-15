import mutagen as mg
from mutagen.flac import FLAC
from bs4 import BeautifulSoup
import urllib.request
import glob
import sys
SUPPORTEDFILES =(".flac",".ogg",".mp3")
def url_contructor(artist,track):
     # example : https://genius.com/Ariana-grande-7-rings-lyrics
     url = "https://genius.com/" + artist[0].replace(" ","-").lower() + "-" + track[0].replace(" ","-").lower() + "-lyrics"
     print(url)
     return url

def get_lyrics(artist,track):
     html = ""
     try :
          req = urllib.request.Request(url_contructor(artist,track),headers={'User-Agent' : "Magic Browser"})
          html = urllib.request.urlopen(req)
     except urllib.error.HTTPError:
          print("HTTP Error")
          return ""
     except urllib.error.URLError:
          print("Incorect URL ")
          return ""
     
     soup = BeautifulSoup(html,features="html.parser")
     #print(soup.prettify())
     soup = soup.find("div",attrs={"class" : "lyrics"})
     soup = soup.get_text(separator=" ")
     print(soup)
     return soup


fileList = []
for ext in  (SUPPORTEDFILES):
     fileList.append(glob.glob("**/*"+ext,recursive=True))
#in case flac:
for y in range (len(fileList[0])):
     currentFile  = FLAC(fileList[0][y])
     print(str(currentFile))
     currentFile["UNSYNCEDLYRICS"] = get_lyrics(currentFile["Artist"],currentFile["title"])
     currentFile.save()
