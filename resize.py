import os, sys
from PIL import Image
import PIL

width = 1920
height = 1280

outfile = 'out.jpg'
infile = 'data/Bali-20231218-175142.jpg'

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
