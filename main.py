import mutagen as mg
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.easymp4 import EasyMP4
from mutagen.easyid3 import EasyID3
import glob
import sys
import multiprocessing
from FilesTools import SearchMusicFiles , GetLyricsFromFile ,SetLyricsToFiles
import time
from LyricsTools import GetLyrics
from Options import JobLimit, SUPPORTEDFILES,  LYRICSTAGS
import os

TOTALFILES = 0





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
