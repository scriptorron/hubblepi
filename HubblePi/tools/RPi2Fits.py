import sys
import os
import os.path
import glob


import HubblePi.Toolbox
import HubblePi.FitsTools


def ConvertRPi2Fits(FileBaseName, Verbose=True):
    if Verbose:
        print(FileBaseName, end='')
    InfoFileName = FileBaseName + ".info"
    RawFileName = FileBaseName + ".jpg"
    if os.path.isfile(InfoFileName) and os.path.isfile(RawFileName):
        FileInfo = HubblePi.Toolbox.LoadInfo(InfoFileName)
        FileData = HubblePi.Toolbox.LoadRawJpg(RawFileName, CameraType=FileInfo["CameraType"])
        HubblePi.FitsTools.SaveFits(FileBaseName + '.fits', FileData, FileInfo)
        if Verbose:
            print("--> Ok.")
        return True
    else:
        if Verbose:
            print("--> Not *.jpg and *.info found!")
        return False


def ConvertAllInPaths(PathList=[], Verbose=True):
    for DataPath in PathList:
        RawFiles = glob.glob(os.path.join(DataPath, "*.info"))
        for RawFile in RawFiles:
            RawFile = RawFile[:-5]
            ConvertRPi2Fits(RawFile, Verbose=Verbose)


def main():
    # command line parameter
    import argparse

    parser = argparse.ArgumentParser(description="HubblePi *.jpg to *.fits converter")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show verbose messages')
    parser.add_argument('FilesOrPaths', nargs='+', type=str,
                        help='*.jpg files or path to many *.jpg files to convert')
    args = parser.parse_args()
    #
    RetCode = 0
    for FileOrPath in args.FilesOrPaths:
        if os.path.isdir(FileOrPath):
            ConvertAllInPaths(PathList=[FileOrPath], Verbose=args.verbose)
        elif os.path.isfile(FileOrPath):
            if FileOrPath.endswith(".jpg"):
                ConvertRPi2Fits(FileOrPath[:-4], Verbose=args.verbose)
            elif FileOrPath.endswith(".info"):
                ConvertRPi2Fits(FileOrPath[:-5], Verbose=args.verbose)
            else:
                print("ERROR: %s not valid type!" % FileOrPath)
                RetCode = -1
        else:
            print("ERROR: %s not valid file or path!" % FileOrPath)
            RetCode = -1
    sys.exit(RetCode)


if __name__ == '__main__':
    main()