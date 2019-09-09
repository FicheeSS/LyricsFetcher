from bs4 import BeautifulSoup
import urllib.request
import re
from Options import URL_CARSET 


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
          req = urllib.request.Request(UrlConstructor(artist,track),headers={'User-Agent' : "Magic Browser"})
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
     soup = BeautifulSoup(html,features="html.parser").find("div",attrs={"class" : "lyrics"}).get_text(separator=" ")
     return soup