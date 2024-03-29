from random import shuffle

import tqdm as tqdm
from clint.textui import puts, colored, progress
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

SUPPORTEDFILES = (".flac", ".ogg", ".mp3", ".m4a", ".mp4")
LYRICSTAGS = ("UNSYNCEDLYRICS", "LYRICS")
URL_CARSET = [("ä", "a"), (" ", "-"), ("'", ""), (",", ""), ("/", "-"), (".", ""), ("û", "u"), ("ü", "u"), ("ù", "u"),
              ("?", ""), ("&", "and"), (":", "")]

DEBUG = False
FORCERE = True
TOTALFILES = 0


def bogosort(l: list) -> list:
    sorted = l
    sorted.sort()
    while sorted != l:
        shuffle(l)
    return l


def UrlConstructor(artist, track):
    # puts(track[0])
    artist[0] = artist[0].lower()
    track[0] = track[0].lower()
    regexparen = re.compile(".*?\((.*?)\)")
    regexcrochet = re.compile(".*?\[.*?\]")
    artist[0] = re.sub("[\(\[].*?[\)\]]", "", artist[0])
    track[0] = re.sub("[\(\[].*?[\)\]]", "", track[0])
    track[0] = track[0].strip()
    artist[0] = artist[0].strip()
    for delete in re.findall(regexparen, track[0]):
        track[0] = str(track[0]).replace(str(delete), "").replace("(", "").replace(")", "")
    for delete in re.findall(regexcrochet, artist[0]):
        artist[0] = str(artist[0]).replace(str(delete), "").replace("[", "").replace("]", "")
    track[0] = str(track[0]).rstrip()
    for carset in URL_CARSET:
        track[0] = track[0].replace(carset[0], carset[1])
        artist[0] = artist[0].replace(carset[0], carset[1])
    url = "https://genius.com/" + artist[0].lower() + "-" + track[0].lower() + "-lyrics"
    return url


def GetLyrics(artist, track):
    html = ""
    try:
        url = UrlConstructor(artist, track)
        if not url:
            return ""
        req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
        html = urllib.request.urlopen(req)
    except urllib.error.HTTPError:
        DEBUG and puts("Lyrics not found " + str(artist) + " " + str(track))
        return ""
    except urllib.error.URLError:
        DEBUG and puts("Incorect URL for " + str(UrlConstructor(artist, track)))
        return ""
    except UnicodeEncodeError:
        DEBUG and puts("Non-Ascii symbol in " + str(artist) + " " + str(track))
        return ""
    try:
        soup = BeautifulSoup(html, features="html.parser").select("[data-lyrics-container=true]")[0].get_text(
            separator=" ")
    except:
        soup = ""
    finally:
        return soup


def GetLyricsInFiles(MFile):
    lyrics = None
    i = 0
    for LyricsTags in LYRICSTAGS:
        try:
            lyrics = MFile[LyricsTags]
        except TypeError:
            if 0 == len(LYRICSTAGS):
                DEBUG and puts("Malformed lyrics")
            else:
                i += 1
        except KeyError:
            try:
                # case ID3
                lyrics = MFile["lyricist"]
            except:
                # case MP4 only works with modified mutagen EasyMP4 library
                try:
                    lyrics = MFile["lyrics"]
                except:
                    pass
    return lyrics


def SearchMusicFiles(dir):
    fileList = []
    ProcessFile = []
    for ext in (SUPPORTEDFILES):
        fileList.append(glob.glob((dir + "/**/*" + ext), recursive=True))

    for SFiles in SUPPORTEDFILES:
        if SFiles == ".flac":
            for y in range(len(fileList[0])):
                try:
                    MFile = FLAC(fileList[0][y])
                    (not GetLyricsInFiles(MFile) or FORCERE) and ProcessFile.append(MFile)
                except:
                    continue
        elif SFiles == ".ogg":
            for y in range(len(fileList[1])):
                MFile = OggVorbis(fileList[1][y])
                (not GetLyricsInFiles(MFile) or FORCERE) and ProcessFile.append(MFile)
        elif SFiles == ".mp3":
            for y in range(len(fileList[2])):
                try:
                    MFile = EasyID3(fileList[2][y])
                    (not GetLyricsInFiles(MFile) or FORCERE) and ProcessFile.append(MFile)
                except:
                    MFile = MP3(fileList[2][y])
                    (not GetLyricsInFiles(MFile) or FORCERE) and ProcessFile.append(MFile)
        elif SFiles == ".m4a" or SFiles == ".mp4":
            for y in range(len(fileList[3])):
                MFile = EasyMP4(fileList[3][y])
                (not GetLyricsInFiles(MFile) or FORCERE) and ProcessFile.append(MFile)
            for y in range(len(fileList[4])):
                MFile = EasyMP4(fileList[4][y])
                (not GetLyricsInFiles(MFile) or FORCERE) and ProcessFile.append(MFile)
    return ProcessFile


def GetLyricsFromFile(MFile):
    try:
        lyrics = GetLyrics(MFile["artist"], MFile["title"])
    except KeyError:
        try:
            lyrics = GetLyrics(MFile["Artist"], MFile["Title"])
        except KeyError:
            DEBUG and puts("File is lacking at least one tags ")
            return ""
        return lyrics
    return lyrics


def SetLyricsToFiles(MFile):
    lyrics = GetLyricsFromFile(MFile)
    i = 0
    if len(lyrics) != 0:
        for LyricsTags in LYRICSTAGS:
            try:
                MFile[LyricsTags] = lyrics
                MFile.save()
            except TypeError:
                if i == len(LYRICSTAGS):
                    DEBUG and puts("Malformed lyrics")
                    # Nfailedfiles += 1
                else:
                    i += 1
            except KeyError:
                try:
                    # case ID3
                    MFile["lyricist"] = lyrics
                    MFile.save()
                except:
                    # case MP4 only works with modified mutagen EasyMP4 library
                    try:
                        MFile["lyrics"] = lyrics
                        MFile.save()
                    except:
                        pass


if __name__ == '__main__':
    args = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--localisation", dest='loc', type=str, help='process file location ')
    try:
        args = parser.parse_args()
    finally:
        if not args or not args.loc or not os.path.exists(args.loc):
            puts("Using current working directory")
            ProcessFile = SearchMusicFiles(os.getcwd())
        else:
            puts("Using provided directory")
            ProcessFile = SearchMusicFiles(args.loc)
    startupTime = time.time()
    puts(colored.red(str(len(ProcessFile))) + " files found")
    jobs = []
    total = 0
    with multiprocessing.Pool() as pool:
        for _ in tqdm.tqdm(pool.imap_unordered(SetLyricsToFiles, ProcessFile), total=len(ProcessFile), colour='green',
                           unit='songs'):
            pass

    timeTaken = time.time() - startupTime
    if timeTaken > 60:
        puts("Time taken : " + colored.red(str(round(timeTaken / 60, 0)) + ":" + str(round(timeTaken % 60, 0))))
    else:
        puts("Time taken : " + colored.red(str(round((time.time() - startupTime), 2)) + " s"))
    puts(colored.green("All files have been processed "))
    sys.exit(0)
