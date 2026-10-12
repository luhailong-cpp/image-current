from workflow import *
from PIL import Image
folder=ROOT/'qa/roof-f02-full-trial';folder.mkdir(exist_ok=True)
im=Image.open(ROOT/'tiles/r09_c12.candidate-v07.png').convert('RGB')
src=Image.open(ROOT/'native/r09_c12_roof_surface_f_v02.png').convert('RGB')
im.paste(src.crop((115,0,1139,1254)),(742,742))
im.save(folder/'r09_c12-trial.png');im.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/'preview.png')
for name,box in [('ef',(600,1100,880,1900)),('fd',(1580,740,1900,1900)),('bottom',(742,1800,1766,2180)),('top',(742,614,1766,870))]:im.crop(box).save(folder/(name+'.png'))
print(folder)
