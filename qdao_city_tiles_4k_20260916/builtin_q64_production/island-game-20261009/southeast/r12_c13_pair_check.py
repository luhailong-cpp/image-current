from pathlib import Path
from PIL import Image
import sys
from workflow import ROOT,read,write,sha,now
rc,ver,top,left=sys.argv[1:5];tid='r12_c13';p=ROOT/'native'/f'{tid}_p{rc}_{ver}.png';im=Image.open(p).convert('RGB').crop((115,115,1139,1139));q=ROOT/'qa/r12_c13-progress';items=[]
for side,name in [('north',top),('west',left)]:
 if name=='-':continue
 n=ROOT/'native'/name;ni=Image.open(n).convert('RGB').crop((115,115,1139,1139))
 if side=='north':
  o=Image.new('RGB',(1024,512));a=[0,768,1024,1024];b=[0,0,1024,256];d=[0,256]
 else:
  o=Image.new('RGB',(512,1024));a=[768,0,1024,1024];b=[0,0,256,1024];d=[256,0]
 o.paste(ni.crop(a),(0,0));o.paste(im.crop(b),d);out=q/f'p{rc}-{ver}-{side}.png';o.save(out);items.append({'file':str(out),'sha256':sha(out),'side':side,'neighbor':str(n),'neighborSha256':sha(n),'neighborCoreCrop':a,'thisCoreCrop':b,'thisDestination':d})
write(q/f'p{rc}-{ver}-index.json',{'createdAt':now(),'file':str(p),'sha256':sha(p),'operation':'exact native 1024 core edge crop/paste. No resampling.','items':items,'status':'pending_visual_review'})
print([x['file'] for x in items])

