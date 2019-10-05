from bs4 import BeautifulSoup
import urllib.request
import re
from Options import URL_CARSET


def UrlConstructor(artist, track):
    regexparen = re.compile(".*?\((.*?)\)")
    regexcrochet = re.compile(".*?\[.*?\]")
    track = track[0]
    artist = artist[0]
    for delete in re.findall(regexparen, track):
        track = str(track).replace(str(delete), "").replace(
            "(", "").replace(")", "")
    for delete in re.findall(regexcrochet, track):
        track = str(track).replace(str(delete), "").replace(
            "[", "").replace("]", "")
    track = str(track).rstrip()
    for carset in URL_CARSET:
        track = track.replace(carset[0], carset[1])
        artist = artist.replace(carset[0], carset[1])
    url = "https://genius.com/" + artist.lower() + "-" + track.lower() + "-lyrics"
    return url


def GetLyrics(artist, track):
    html = ""
    try:
        req = urllib.request.Request(UrlConstructor(artist, track), headers={
                                     'User-Agent': "Magic Browser"})
        html = urllib.request.urlopen(req)
    except urllib.error.HTTPError:
        print("Lyrics not found " + str(artist) + " " + str(track))
        return ""
    except urllib.error.URLError:
        print("Incorect URL for "+str(UrlConstructor(artist, track)))
        return ""
    except UnicodeEncodeError:
        print("Non-Ascii symbol in " + str(artist) + " " + str(track))
        return ""
    soup = BeautifulSoup(html, features="html.parser").find(
        "div", attrs={"class": "lyrics"}).get_text(separator=" ")
    return soup
