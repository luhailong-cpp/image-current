"""Assemble accepted same-coordinate paver pixels into r10_c13 v02 with exact source coverage."""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,numpy as np,os
from datetime import datetime,timezone
R=Path(__file__).parent;Q=R/'qa/r10_c13-v02';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stamp=datetime.now(timezone.utc).isoformat();oldsel=read(R/'selected-native-r10_c13.json');cut=[847,0,1222,315];entries=[]
for e in oldsel['entries']:
 d=e['destinationBox'];ix0=max(d[0],cut[0]);iy0=max(d[1],cut[1]);ix1=min(d[2],cut[2]);iy1=min(d[3],cut[3])
 if ix0>=ix1 or iy0>=iy1:entries.append(e);continue
 boxes=[[d[0],d[1],d[2],iy0],[d[0],iy1,d[2],d[3]],[d[0],iy0,ix0,iy1],[ix1,iy0,d[2],iy1]]
 for b in boxes:
  if b[0]>=b[2] or b[1]>=b[3]:continue
  n=dict(e);s=e['sourceCrop'];n['sourceCrop']=[s[0]+b[0]-d[0],s[1]+b[1]-d[1],s[0]+b[2]-d[0],s[1]+b[3]-d[1]];n['destinationBox']=b;entries.append(n)
f=R/'native/r10_c13_paver_v02.png';entries.append({'file':str(f),'sha256':sha(f),'sourceCrop':[450,115,825,430],'destinationBox':cut,'record':str(f)+'.generation.json','reason':'Source-native whole-paver repair; exact affected rectangle removes false small corner and vertical source tone edge. No resize, blending or paint.'})
out=Image.new('RGB',(4096,4096));coverage=np.zeros((4096,4096),dtype=np.uint8)
for e in entries:
 src=Image.open(e['file']);assert src.size==(1254,1254);d=e['destinationBox'];out.paste(src.crop(e['sourceCrop']),d[:2]);coverage[d[1]:d[3],d[0]:d[2]]+=1
assert coverage.min()==coverage.max()==1
for e in entries:assert ImageChops.difference(out.crop(e['destinationBox']),Image.open(e['file']).crop(e['sourceCrop'])).getbbox() is None
dest=R/'tiles/r10_c13.candidate-v02.png';assert not dest.exists();out.save(dest)
sel=dict(oldsel,selectionTime=stamp,entries=entries,sourceCount=len(set(e['file'] for e in entries)),rectangleCount=len(entries),latestCandidate=str(dest),candidateSha256=sha(dest),previousCandidate=str(R/'tiles/r10_c13.candidate.png'),repairNative=str(f))
write(R/'selected-native-r10_c13-v02.json',sel);write(Path(str(dest)+'.generation.json'),dict(sel,file=str(dest),sha256=sha(dest),assembly='Exact original-pixel crop/paste; no resize/blend'))
oldqa=R/'qa/r10_c13-v01';inherit=[]
for p in sorted(oldqa.glob('*.png')):
 name=p.stem
 if name.startswith('v') and len(name)==3:
  row,col=int(name[1]),int(name[2]);x=col*1024;y=(row-1)*1024;im=out.crop((x-256,y,x+256,y+1024))
 elif name.startswith('h') and len(name)==3:
  row,col=int(name[1]),int(name[2]);x=(col-1)*1024;y=row*1024;im=out.crop((x,y-256,x+1024,y+256))
 elif name.startswith('junction_'):
  row,col=int(name[-2]),int(name[-1]);x=col*1024;y=row*1024;im=out.crop((x-256,y-256,x+256,y+256))
 else:continue
 im.save(Q/p.name);same=ImageChops.difference(im,Image.open(p)).getbbox() is None;inherit.append({'file':str(Q/p.name),'unchangedFromV01':same,'alreadyViewedV01':True})
parents={'NW':R/'tiles/r09_c12.candidate-v02.png','NE':R/'tiles/r09_c13.candidate.png','SW':R/'tiles/r10_c12.candidate-v02.png','SE':dest}
ims={k:Image.open(v) for k,v in parents.items()}
for name,a,b,vertical in [('top','NE','SE',False),('left','SW','SE',True),('north-left','NW','NE',True),('west-top','NW','SW',False)]:
 for i in range(4):
  p=i*1024
  if vertical:
   im=Image.new('RGB',(512,1024));im.paste(ims[a].crop((3840,p,4096,p+1024)),(0,0));im.paste(ims[b].crop((0,p,256,p+1024)),(256,0))
  else:
   im=Image.new('RGB',(1024,512));im.paste(ims[a].crop((p,3840,p+1024,4096)),(0,0));im.paste(ims[b].crop((p,0,p+1024,256)),(0,256))
  fn=f'border-{name}-{i+1}.png';im.save(Q/fn);inherit.append({'file':str(Q/fn),'unchangedFromV01':ImageChops.difference(im,Image.open(oldqa/fn)).getbbox() is None,'alreadyViewedV01':True})
cross=Image.new('RGB',(1024,1024));cross.paste(ims['NW'].crop((3584,3584,4096,4096)),(0,0));cross.paste(ims['NE'].crop((0,3584,512,4096)),(512,0));cross.paste(ims['SW'].crop((3584,0,4096,512)),(0,512));cross.paste(ims['SE'].crop((0,0,512,512)),(512,512));cross.save(Q/'four-tile-junction.png');inherit.append({'file':str(Q/'four-tile-junction.png'),'unchangedFromV01':ImageChops.difference(cross,Image.open(oldqa/'four-tile-junction.png')).getbbox() is None,'alreadyViewedV01':True})
context=Image.new('RGB',(675,580));context.paste(ims['NE'].crop((697,3981,1372,4096)),(0,0));context.paste(out.crop((697,0,1372,465)),(0,115));context.save(Q/'repair-boundaries.png')
audit=[]
for f in sorted((R/'native').glob('r10_c13*.png')):
 rec=read(Path(str(f)+'.generation.json'));pp=Path(rec['prompt']);receipt=read(R/rec['evidence']['toolReceipt'])
 checks={'nativeHash':sha(f)==rec['sha256'],'sourceHash':sha(Path(rec['sourceOutputPath']))==rec['sourceOutputSha256'],'promptHash':sha(pp)==rec['promptSha256'],'promptExact':receipt['submittedArguments']['prompt'].replace('\r\n','\n')==pp.read_text(encoding='utf-8'),'referencesHash':all(sha(Path(x['file']))==x['sha256'] for x in rec['references']),'actualSize':list(Image.open(f).size)==[1254,1254],'modelNull':rec['actualModel'] is None,'qualityNull':rec['actualQuality'] is None}
 assert all(checks.values()),(f,checks);audit.append({'file':str(f),'checks':checks})
write(Q/'source-audit.json',{'candidate':str(dest),'sha256':sha(dest),'entries':entries,'sourceCount':sel['sourceCount'],'rectangleCount':len(entries),'exactCoverageOnce':True,'sourcePixelReplayExact':True,'nativeAttemptCount':len(audit),'nativeAudit':audit,'qaInheritance':inherit,'formalAcceptedCount':0,'borders':{k:{'file':str(v),'sha256':sha(v)} for k,v in parents.items()}})
p=R/'progress-r10_c13.json';d=read(p);d.update(status='candidate_v02_final_visual_check',generatedNativeCount=len(audit),complete4kCount=1,formalAcceptedCount=0,updatedAt=stamp,currentPatch=None,latestCandidate=str(dest),nextStep='Verify changed v11, top borders 1/2 and new hard-insert boundaries.');tmp=p.with_suffix('.pending.json');write(tmp,d);os.replace(tmp,p)
print(json.dumps({'candidate':str(dest),'sha256':sha(dest),'sourceCount':sel['sourceCount'],'rectangles':len(entries),'attempts':len(audit),'changedQA':[x['file'] for x in inherit if not x['unchangedFromV01']]}))

