from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent
sys.path.insert(0,str(B));sys.path.insert(0,str(B/'work-r03_c04'))
from assemble_r03_c03 import compose
from apply_r03_c04_repairs import window_mask
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def arr(p):return np.array(Image.open(p).convert('RGB'))
def assemble(tag):
 O=W/tag;O.mkdir(exist_ok=True);Q=O/'qa';Q.mkdir(exist_ok=True)
 sources=[];arrays={};seen={}
 def add(p):
  p=Path(p);key=str(p.resolve()).lower()
  if key in seen:return seen[key]
  r=read(str(p)+'.generation.json');sid=len(sources)+1
  assert sha(p)==r['sha256'] and r['route']=='builtin' and r['nativeScaleResampled']==False
  a=arr(p);assert a.shape==(1254,1254,3)
  for ref in r['references']:
   assert sha(ref['file'])==ref['sha256'],str(ref['file'])
  for ep in [r['prompt'],r['evidence']['request'],r['evidence']['receipt']]:assert Path(ep).exists()
  rec=read(r['evidence']['receipt']);assert sha(rec['originalFile'])==sha(p)
  info={'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'globalNativeBox':r['globalNativeBox'],'nativeScaleResampled':False,'actualModel':None,'actualQuality':None}
  sources.append(info);arrays[sid]=a;seen[key]=sid;return sid
 patches=[]
 for row in range(1,5):
  for col in range(1,5):
   s=read(W/'selections'/f's{row:02d}_s{col:02d}.json');sid=add(s['file']);assert sid==(row-1)*4+col
   patches.append(arrays[sid])
 pixels,ids,seams=compose(patches);ids=ids.astype(np.uint16)
 J=B/'work-r04_c04/joint-west/final-v3';jr=read(J/'joint-assembly.json')
 n=arr(J/'r05_c03.first-row.joint-proposal.png');nid=np.array(Image.open(J/'r05_c03.first-row.source-id.png'))
 mapped=np.zeros_like(nid,dtype=np.uint16)
 used=set(int(x) for x in np.unique(nid))
 for s in jr['sources']:
  if s['jointSourceId'] in used:mapped[nid==s['jointSourceId']]=add(s['file'])
 assert mapped.min()>0
 # Preserve the authoritative north row except where the native row2 hard cut already owns its southern overlap.
 take=(ids[:1024]<=4)|(mapped>16)
 inherited_changed=int(np.any(pixels[:1024]!=n,axis=2)[take].sum())
 pixels[:1024][take]=n[take];ids[:1024][take]=mapped[take]
 overlays=[];plan=read(W/'resume-overlays.json') if (W/'resume-overlays.json').exists() else []
 for ov in plan:
  sid=add(ov['file']);a=arrays[sid];g=sources[sid-1]['globalNativeBox'];x,y=g[0]-8192,g[1]-16384
  region=pixels[y:y+1254,x:x+1254];assert region.shape==a.shape
  mask,path=window_mask(region,a,ov['window'])
  region[mask]=a[mask];ids[y:y+1254,x:x+1254][mask]=sid
  mp=O/(ov['id']+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp)
  overlays.append({**ov,'sourceId':sid,'globalNativeBox':g,'mask':str(mp),'maskSha256':sha(mp),'selectedPixels':int(mask.sum()),'paths':path})
 Image.fromarray(pixels).save(O/'r05_c03.candidate.png')
 Image.fromarray(ids).save(O/'r05_c03.source-id.png')
 write(O/'seams.json',seams)
 counts=[];replay=np.zeros_like(pixels)
 for s in sources:
  sid=s['sourceId'];yy,xx=np.nonzero(ids==sid);g=s['globalNativeBox'];sx=xx+8192-g[0];sy=yy+16384-g[1]
  assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254))
  replay[yy,xx]=arrays[sid][sy,sx]
  counts.append({'sourceId':sid,'pixelCount':int(xx.size)})
 mismatch=int(np.any(replay!=pixels,axis=2).sum());assert mismatch==0
 proof={'verifiedPixels':int(ids.size),'pixelMismatches':mismatch,'allPixelsNativeExact':True,'uncovered':int((ids==0).sum()),'sources':counts}
 write(O/'replay-proof.json',proof)
 rec={'tile':'r05_c03','createdAt':datetime.now(timezone.utc).isoformat(),'status':'candidate-pending-full-native-visual-QA','formalAccepted':False,'globalCoreBox':[8192,16384,12288,20480],'candidate':{'file':str(O/'r05_c03.candidate.png'),'sha256':sha(O/'r05_c03.candidate.png')},'sourceIdMap':{'file':str(O/'r05_c03.source-id.png'),'sha256':sha(O/'r05_c03.source-id.png'),'coordinateFormula':'nativeX=outputX+8192-globalNativeBox[0]; nativeY=outputY+16384-globalNativeBox[1]'},'sources':sources,'composition':{'method':'integer-native overlap hard cuts, authoritative north row inheritance then local native windows','resample':False,'feather':False,'paint':False,'colorMatching':False},'northInheritance':{'assembly':str(J/'joint-assembly.json'),'candidate':str(J/'r05_c03.first-row.joint-proposal.png'),'sourceIds':str(J/'r05_c03.first-row.source-id.png'),'rule':'inherit while base row1 owns pixel or joint repair source owns pixel; retain southern native row2 overlap cut','changedPixels':inherited_changed},'overlays':overlays,'proof':{'file':str(O/'replay-proof.json'),'sha256':sha(O/'replay-proof.json')},'script':{'file':str(Path(__file__)),'sha256':sha(__file__)}}
 write(O/'assembly.json',rec)
 for k in (1,2,3):
  for j in range(4):
   Image.fromarray(pixels[j*1024:(j+1)*1024,k*1024-200:k*1024+200]).save(Q/f'v{k}-{j+1}.100pct.png')
   Image.fromarray(pixels[k*1024-200:k*1024+200,j*1024:(j+1)*1024]).save(Q/f'h{k}-{j+1}.100pct.png')
 for y in (1024,2048,3072):
  for x in (1024,2048,3072):Image.fromarray(pixels[y-260:y+260,x-260:x+260]).save(Q/f'junction-{x}-{y}.100pct.png')
 Image.fromarray(pixels).resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-review-only.png')
 print(json.dumps({'candidate':str(O/'r05_c03.candidate.png'),'sources':len(sources),'proof':proof,'inheritedChangedPixels':inherited_changed}))
if __name__=='__main__':assemble(sys.argv[1])

