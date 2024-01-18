import os, sys
from PIL import Image
import PIL

width = 1920
height = 1280

def resize ():
    outfile = 'dataout/out.jpg'
    infile = 'data/Bali-20231218-180015.jpg'

    #   factor-H = actual-H / desired-H
    #   factor-V = actual-V / desired-V
    #   factor = max (factor-H, factor-V)
    #   if factor < 1  =>  don't resize
    #   else final-H = actual-H / factpr, final-V = actual-V / factor

    img = Image.open (infile)
    wpercent = (width / float (img.size[0]))
    hsize = int ((float (img.size[1]) * float (wpercent)))
    img = img.resize ((width, hsize), PIL.Image.LANCZOS)
    img.save (outfile)

def recurseDir ():
    folder = "data"

    for root, dirs, files in os.walk(folder):
        path = root.split (os.sep)
        # print ((len(path) - 1) * '---', os.path.basename (root))
        print ((len(path) - 1) * '---', root)
        for file in files:
            print (len(path) * '---', file)

# recurseDir ()
resize ();
