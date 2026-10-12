"""Exact source-rectangle assembly and QA crops for r10_c13 only."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,numpy as np,os
from datetime import datetime,timezone
R=Path(__file__).parent;T='r10_c13';Q=R/'qa'/f'{T}-v01';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat()
versions={'13':'v02','14':'v03'}
entries=[]
for row in range(1,5):
 for col in range(1,5):
  p=f'{row}{col}';f=R/'native'/f'{T}_p{p}_{versions.get(p,"v01")}.png'
  x=(col-1)*1024;y=(row-1)*1024
  sy=230 if p=='11' else 115;dy=y+115 if p=='11' else y
  entries.append({'file':str(f),'sha256':sha(f),'sourceCrop':[115,sy,1139,1139],'destinationBox':[x,dy,x+1024,y+1024],'record':str(f)+'.generation.json'})
f=R/'native'/'r09_c13_p41_v02.png'
entries.append({'file':str(f),'sha256':sha(f),'sourceCrop':[115,1139,1139,1254],'destinationBox':[0,0,1024,115],'record':str(f)+'.generation.json','reason':'Real same-coordinate south halo ownership; avoid invented wood foot in r10p11 top 115 core.'})
out=Image.new('RGB',(4096,4096));coverage=np.zeros((4096,4096),dtype=np.uint8)
for e in entries:
 im=Image.open(e['file']);assert im.size==(1254,1254)
 crop=im.crop(e['sourceCrop']);d=e['destinationBox'];assert crop.size==(d[2]-d[0],d[3]-d[1]);out.paste(crop,d[:2]);coverage[d[1]:d[3],d[0]:d[2]]+=1
assert coverage.min()==coverage.max()==1
dest=R/'tiles'/f'{T}.candidate.png';assert not dest.exists();out.save(dest)
for e in entries:
 assert ImageChops.difference(out.crop(e['destinationBox']),Image.open(e['file']).crop(e['sourceCrop'])).getbbox() is None
sel={'tile':T,'selectionTime':stamp,'entries':entries,'sourceCount':len(entries),'exactRectangleCoverageOnce':True,'sourcePixelsReplayExact':True,'nativeCoreSize':1024,'canvasSize':[4096,4096],'resizedFinalArtwork':False,'formalAcceptedCount':0}
write(R/f'selected-native-{T}.json',sel)
write(Path(str(dest)+'.generation.json'),dict(sel,file=str(dest),sha256=sha(dest),assembly='Exact original-pixel crop/paste only, no resize/blend/repaint'))
for row in range(1,5):
 for col in range(1,4):
  x=col*1024;y=(row-1)*1024;out.crop((x-256,y,x+256,y+1024)).save(Q/f'v{row}{col}.png')
for row in range(1,4):
 for col in range(1,5):
  x=(col-1)*1024;y=row*1024;out.crop((x,y-256,x+1024,y+256)).save(Q/f'h{row}{col}.png')
for row in range(1,4):
 for col in range(1,4):
  x=col*1024;y=row*1024;out.crop((x-256,y-256,x+256,y+256)).save(Q/f'junction_{row}{col}.png')
out.crop((0,0,1024,371)).save(Q/'shifted-top-ownership.png')
parents={'NW':R/'tiles'/'r09_c12.candidate-v02.png','NE':R/'tiles'/'r09_c13.candidate.png','SW':R/'tiles'/'r10_c12.candidate-v02.png','SE':dest}
ims={k:Image.open(v) for k,v in parents.items()}
for name,a,b,vertical in [('top','NE','SE',False),('left','SW','SE',True),('north-left','NW','NE',True),('west-top','NW','SW',False)]:
 for i in range(4):
  p=i*1024
  if vertical:
   strip=Image.new('RGB',(512,1024));strip.paste(ims[a].crop((3840,p,4096,p+1024)),(0,0));strip.paste(ims[b].crop((0,p,256,p+1024)),(256,0))
  else:
   strip=Image.new('RGB',(1024,512));strip.paste(ims[a].crop((p,3840,p+1024,4096)),(0,0));strip.paste(ims[b].crop((p,0,p+1024,256)),(0,256))
  strip.save(Q/f'border-{name}-{i+1}.png')
cross=Image.new('RGB',(1024,1024))
cross.paste(ims['NW'].crop((3584,3584,4096,4096)),(0,0));cross.paste(ims['NE'].crop((0,3584,512,4096)),(512,0));cross.paste(ims['SW'].crop((3584,0,4096,512)),(0,512));cross.paste(ims['SE'].crop((0,0,512,512)),(512,512));cross.save(Q/'four-tile-junction.png')
audit=[]
for f in sorted((R/'native').glob(T+'*.png')):
 rec=read(Path(str(f)+'.generation.json'));prompt=Path(rec['prompt']);receipt=read(R/rec['evidence']['toolReceipt'])
 checks={'nativeHash':sha(f)==rec['sha256'],'sourceOutputHash':sha(Path(rec['sourceOutputPath']))==rec['sourceOutputSha256'],'promptHash':sha(prompt)==rec['promptSha256'],'promptExact':receipt['submittedArguments']['prompt'].replace('\r\n','\n')==prompt.read_text(encoding='utf-8'),'refsHash':all(sha(Path(x['file']))==x['sha256'] for x in rec['references']),'actualSize':list(Image.open(f).size)==[1254,1254],'actualModelNull':rec['actualModel'] is None,'actualQualityNull':rec['actualQuality'] is None}
 assert all(checks.values()),(str(f),checks);audit.append({'file':str(f),'checks':checks})
report={'tile':T,'createdAt':stamp,'candidate':str(dest),'sha256':sha(dest),'nativeAttemptCount':len(audit),'coordinateCount':16,'selectedSourceCount':17,'nativeAudit':audit,'pixelReplayExact':True,'coverageOnce':True,'borders':{k:{'file':str(v),'sha256':sha(v)} for k,v in parents.items()},'qaStatus':'pending_visual_review','formalAcceptedCount':0}
write(Q/'source-audit.json',report)
prog=R/f'progress-{T}.json';d=read(prog);d.update(status='candidate_assembled_pending_visual_QA',generatedNativeCount=len(audit),usableNativeCount=16,complete4kCount=1,formalAcceptedCount=0,currentPatch=None,updatedAt=stamp,nextStep='Inspect all actual seams and 2x2 shared borders; repair actionable defects.');tmp=prog.with_suffix('.pending.json');write(tmp,d);os.replace(tmp,prog)
print(json.dumps({'candidate':str(dest),'sha256':sha(dest),'nativeAttempts':len(audit),'sourceRectangles':len(entries),'qa':str(Q)}))

