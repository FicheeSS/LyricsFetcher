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