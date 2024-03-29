import os, sys
from PIL import Image
import PIL
import shutil
import imghdr

desiredWidth = 1920
desiredHeight = 1280
srcFolder = '_select'
dstFolder = 'reduced'


def resize (infile, outfile):
    print (infile)

    if (not imghdr.what (infile)):
        shutil.copy (infile, outfile)
        return

    img = Image.open (infile)

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break;
    exif = img._getexif ()
    if exif[orientation] == 3:
        img = img.rotate (180, expand=True)
    elif exif[orientation] == 6:
        img = img.rotate (270, expand=True)
    elif exif[orientation] == 8:
        img = img.rotate (90, expand=True)

    factorW = img.size[0] / desiredWidth
    factorH = img.size[1] / desiredHeight
    factor = max (factorW, factorH)

    if (factor < 1):
        shutil.copy (infile, outfile)
    else:
        finalW = int (img.size[0] / factor)
        finalH = int (img.size[1] / factor)
        img = img.resize ((finalW, finalH), PIL.Image.LANCZOS)
        img.save (outfile)


def recurseDir ():
    for root, dirs, files in os.walk(srcFolder):
        path = root.split (os.sep)
        srcPath = os.sep.join (path)
        dstPath = srcPath.replace(srcFolder, dstFolder, 1)
        os.makedirs (dstPath, exist_ok = True)

        for file in files:
            infile = srcPath + os.sep + file
            outfile = dstPath + os.sep + file
            resize (infile, outfile)


recurseDir ()
