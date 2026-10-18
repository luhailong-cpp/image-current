from workflow import ROOT,read,write,sha,now
from PIL import Image
import sys
name=sys.argv[1];q=ROOT/'qa/right-current-20261013';q.mkdir(exist_ok=True);s=ROOT/'native'/f'{name}.png';im=Image.open(s).convert('RGB').crop((115,115,1139,1139));a=[]
for spec in sys.argv[2:]:
 side,n=spec.split('=');np=ROOT/'native'/f'{n}.png';ni=Image.open(np).convert('RGB').crop((115,115,1139,1139))
 if side=='N':o=Image.new('RGB',(1024,512));o.paste(ni.crop((0,768,1024,1024)),(0,0));o.paste(im.crop((0,0,1024,256)),(0,256))
 elif side=='S':o=Image.new('RGB',(1024,512));o.paste(im.crop((0,768,1024,1024)),(0,0));o.paste(ni.crop((0,0,1024,256)),(0,256))
 elif side=='E':o=Image.new('RGB',(512,1024));o.paste(im.crop((768,0,1024,1024)),(0,0));o.paste(ni.crop((0,0,256,1024)),(256,0))
 elif side=='W':o=Image.new('RGB',(512,1024));o.paste(ni.crop((768,0,1024,1024)),(0,0));o.paste(im.crop((0,0,256,1024)),(256,0))
 else:raise ValueError(side)
 f=q/f'{name}-{side}.png';o.save(f);a.append({'file':str(f),'sha256':sha(f),'source':str(s),'sourceSha256':sha(s),'neighbor':str(np),'neighborSha256':sha(np),'side':side,'resampled':False})
write(q/f'{name}-pairs.json',{'atUtc':now(),'pairs':a,'passed':None});print([str(x['file']) for x in a])
