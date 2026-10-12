from workflow import *
from PIL import Image
base=Image.open(ROOT/'tiles/r09_c12.candidate-v04.png').convert('RGB');src=Image.open(ROOT/'native/r09_c12_roof_surface_d_v01.png').convert('RGB');base.paste(src,(1651,742));folder=ROOT/'qa/roof-surface-v01'
for name,box in {'d-full-top':[1651,614,2905,870],'d-full-bottom':[1651,1868,2905,2124],'d-full-left-a':[1523,742,1779,1369],'d-full-left-b':[1523,1369,1779,1996],'d-full-right-a':[2777,742,3033,1369],'d-full-right-b':[2777,1369,3033,1996]}.items():base.crop(box).save(folder/(name+'.png'))

