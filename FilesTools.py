import glob
from Options import SUPPORTEDFILES
import mutagen as mg
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.easymp4 import EasyMP4
from mutagen.easyid3 import EasyID3


def SearchMusicFiles(dir):
    fileList = []
    ProcessFile = []
    for ext in (SUPPORTEDFILES):
        fileList.append(glob.glob((dir+"/**/*"+ext), recursive=True))
    for SFiles in SUPPORTEDFILES:
        if SFiles == ".flac":
            for y in range(len(fileList[0])):
                ProcessFile.append(FLAC(fileList[0][y]))
        elif SFiles == ".ogg":
            for y in range(len(fileList[1])):
                ProcessFile.append(OggVorbis(fileList[1][y]))
        elif SFiles == ".mp3":
            for y in range(len(fileList[2])):
                try:
                    ProcessFile.append(EasyID3(fileList[2][y]))
                except:
                    ProcessFile.append(MP3(fileList[2][y]))
        elif SFiles == ".m4a" or SFiles == ".mp4":
            for y in range(len(fileList[3])):
                ProcessFile.append(EasyMP4(fileList[3][y]))
            for y in range(len(fileList[4])):
                ProcessFile.append(EasyMP4(fileList[4][y]))
    return ProcessFile
