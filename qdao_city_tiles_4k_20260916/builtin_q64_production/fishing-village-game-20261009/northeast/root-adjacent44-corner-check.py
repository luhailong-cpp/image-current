from r06_c13_extension import *
from PIL import Image,ImageDraw
a=Image.open(Z/'native/r07_c12_northrepair43-v1.png').convert('RGB').crop((1024,0,1254,230))
b=Image.open(Z/'native/resume-20261010-stall-upper-v1.png').convert('RGB').crop((0,1024,230,1254))
q=Image.new('RGB',(460,230));q.paste(a,(0,0));q.paste(b,(230,0));q.save(Z/'qa/root-adjacent44-top-left-anchor-comparison.png')
