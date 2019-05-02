import mutagen as mg
import bs4 as bs
import glob
import sys,getopt

def usage():
    print("Usage : ")
    print("       -i <path to the folder>")
    print("       -h show this help")
    print("       -v show verbose")

def input():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:v", ["help","input="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i","--input"):
            input = a
            print("input = " + input)
            return input 
        else:
            assert False, "unhandled option"

if len(input()) == 0:
    print("input option empty")
    sys.exit(2)
else : 
    