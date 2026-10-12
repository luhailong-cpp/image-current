from pathlib import Path
from PIL import Image
import json,hashlib
d=Path(__file__).parent
q=d/'qa/final-v2';q.mkdir(exist_ok=True)
candidate=d/'candidate/r05_c10-4096-candidate-v2.png'
im=Image.open(candidate).convert('RGB');assert im.size==(4096,4096)
northpath=d.parent/'r04_c10/candidate/r04_c10-4096-candidate-v2.png'
north=Image.open(northpath).convert('RGB')
sources=[]
for a in [1024,2048,3072]:
 v=Image.new('RGB',(1024,1024));h=Image.new('RGB',(1024,1024))
 for i in range(4):
  vc=im.crop((a-128,i*1024,a+128,(i+1)*1024));hc=im.crop((i*1024,a-128,(i+1)*1024,a+128))
  vp=q/f'vertical-x{a}-y{i*1024}.png';hp=q/f'horizontal-y{a}-x{i*1024}.png'
  vc.save(vp);hc.save(hp);sources.extend([str(vp),str(hp)])
  v.paste(vc,(i*256,0));h.paste(hc,(0,i*256))
 v.save(q/f'vertical-x{a}-native-atlas.png');h.save(q/f'horizontal-y{a}-native-atlas.png')
for i in range(4):
 c=Image.new('RGB',(1024,256));c.paste(north.crop((i*1024,3968,(i+1)*1024,4096)),(0,0));c.paste(im.crop((i*1024,0,(i+1)*1024,128)),(0,128));p=q/f'north-seam-{i+1}-native.png';c.save(p);sources.append(str(p))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(q/'qa-sources.json').write_text(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'northCandidate':str(northpath),'northSha256':sha(northpath),'count':len(sources),'nativePixelsResized':False,'files':sources},indent=2)+'\n')
print(json.dumps({'directory':str(q),'nativeSeamCount':len(sources),'atlases':6}))

