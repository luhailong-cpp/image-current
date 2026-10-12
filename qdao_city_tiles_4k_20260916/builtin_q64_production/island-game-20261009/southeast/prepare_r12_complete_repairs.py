from workflow import *
from PIL import Image
jobs=[('r12_c12_p32','v04','r12_c12_p32_v02.png',[('r12_c12_p32_v03.png',[0,0,600,1254],[0,0])]),('r12_c12_p13','v05','r12_c12_p13_v04.png',[('r12_c12_p12_v02.png',[1024,0,1254,1254],[0,0])])]
for pid,v,name,overlays in jobs:
 src=ROOT/'native'/name;im=Image.open(src).convert('RGB');parts=[{'file':str(src),'sha256':sha(src),'role':'complete native base'}]
 for nn,crop,dest in overlays:
  f=ROOT/'native'/nn;im.paste(Image.open(f).convert('RGB').crop(crop),dest);parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destination':dest})
 out=ROOT/'guides'/f'{pid}.native-context-{v}.png';assert not out.exists();im.save(out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'operation':'exact native crops for whole-junction edit guide, never final art','sources':parts,'usableAsFinalArt':False})
