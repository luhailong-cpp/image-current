from native_work import *
import sys,re,numpy as np
tids=sys.argv[1:]; assert len(tids)>=2
coords={t:tuple(map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',t).groups())) for t in tids}
images={t:Image.open(ZONE/'tiles'/f'{t}.png').convert('RGB') for t in tids}
records={t:read(ZONE/'tiles'/f'{t}.png.derivation.json') for t in tids}
for t in tids:assert sha(ZONE/'tiles'/f'{t}.png')==records[t]['sha256']
out=ZONE/'qa/connected-area';out.mkdir(exist_ok=True);evidence=[]
for a,(ra,ca) in coords.items():
 for b,(rb,cb) in coords.items():
  if (rb,cb) not in [(ra,ca+1),(ra+1,ca)]:continue
  horizontal=rb==ra
  for i in range(4):
   seg=Image.new('RGB',(512,1024) if horizontal else (1024,512))
   if horizontal:
    seg.paste(images[a].crop((3840,i*1024,4096,(i+1)*1024)),(0,0));seg.paste(images[b].crop((0,i*1024,256,(i+1)*1024)),(256,0))
   else:
    seg.paste(images[a].crop((i*1024,3840,(i+1)*1024,4096)),(0,0));seg.paste(images[b].crop((i*1024,0,(i+1)*1024,256)),(0,256))
   p=out/f'{a}__{b}.segment-{i+1}-100pct.png';seg.save(p);evidence.append({'pair':[a,b],'direction':'left-right' if horizontal else 'top-bottom','segment':i+1,'file':p.as_posix(),'status':'pending'})
r0=min(r for r,c in coords.values());c0=min(c for r,c in coords.values());r1=max(r for r,c in coords.values());c1=max(c for r,c in coords.values())
can=Image.new('RGB',((c1-c0+1)*4096,(r1-r0+1)*4096))
for t,(r,c) in coords.items():can.paste(images[t],((c-c0)*4096,(r-r0)*4096))
if len(tids)==(r1-r0+1)*(c1-c0+1):
 name=f'r{r0:02}-r{r1:02}_c{c0:02}-c{c1:02}';can.save(out/f'{name}.native.png');can.resize((can.width//4,can.height//4),Image.Resampling.LANCZOS).save(out/f'{name}.preview.png')
 for r in range(1,r1-r0+1):
  for c in range(1,c1-c0+1):can.crop((c*4096-512,r*4096-512,c*4096+512,r*4096+512)).save(out/f'{name}.cross-{r}-{c}-100pct.png')
else:name='partial-group'
write(out/f'{name}.json',{'tiles':[{'tileId':t,'sha256':records[t]['sha256'],'worldBox':records[t]['worldBox']} for t in tids],'size':list(can.size),'status':'pending_visual_review','seamEvidence':evidence,'finalArtUpscaled':False,'formalAccepted':False})
print(json.dumps({'group':name,'segments':len(evidence),'nativeSize':list(can.size),'record':(out/f'{name}.json').as_posix()}))

