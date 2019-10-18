import mutagen as mg
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.easymp4 import EasyMP4
from mutagen.easyid3 import EasyID3
import glob
import sys
import multiprocessing
from FilesTools import SearchMusicFiles
import time
from LyricsTools import GetLyrics
from Options import JobLimit, SUPPORTEDFILES,  LYRICSTAGS
import os

TOTALFILES = 0


def GetLyricsFromFile(MFile):
    try:
        lyrics = GetLyrics(MFile["artist"], MFile["title"])
    except KeyError:
        try:
            lyrics = GetLyrics(MFile["Artist"], MFile["Title"])
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
            try:
                MFile[LyricsTags] = lyrics
                MFile.save()
            except TypeError:
                if i == len(LYRICSTAGS):
                    print("Malformed lyrics")
                    #Nfailedfiles += 1
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
                        print(
                            "Please use modified Mutagen EasyMp4 library with lyrics tag")
#     else :
        #Nfailedfiles += 1


if __name__ == '__main__':
    #q = Queue.Queue("50")
    ProcessFile = SearchMusicFiles(os.getcwd())
    print(ProcessFile)
    startupTime = time.time()
    print(str(len(ProcessFile)) + " files found")
    # Cut the ProcessFile list into list of JobLimit size
    JobsFile = []
    for i in range(int(len(ProcessFile)/JobLimit+1)):
        JobsFile.append([])
    for i in range(int(len(ProcessFile)/JobLimit)+1):
        if (len(ProcessFile) - JobLimit * i) > JobLimit:
            for y in range(JobLimit):
                JobsFile[i].append(ProcessFile[(i+1) * y])
        else:
            for y in range(len(ProcessFile) - JobLimit * i):
                JobsFile[i].append(ProcessFile[(i+1) * y])

    jobs = []
    for i in range(len(JobsFile)):
        for y in range(len(JobsFile[i])):
            p = multiprocessing.Process(
                target=SetLyricsToFiles, args=(JobsFile[i][y],))
            p.start()
            jobs.append(p)
        for proc in jobs:
            proc.join()

        print("Batch : " + str(i+1) + " out of : " + str(len(JobsFile)))

    print("Time taken : " + str(time.time() - startupTime))
    print("All files have been processed ")
