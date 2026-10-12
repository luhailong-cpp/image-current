from workflow import *
from PIL import Image
base=Image.open(ROOT/'tiles/r09_c12.candidate-v03.png').convert('RGB');native=Image.open(ROOT/'native/r09_c12_roof_surface_b_v01.png').convert('RGB')
folder=ROOT/'qa/roof-surface-v01'
for y in [115,230,300,345]:
 im=Image.new('RGB',(1024,256));im.paste(base.crop([742,max(0,y-128),1766,y]),(0,128-min(y,128)));im.paste(native.crop([115,y,1139,y+128]),(0,128));im.save(folder/f'b-top-shift-{y}.png')

