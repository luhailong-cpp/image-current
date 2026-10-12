import argparse,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent
C=json.loads((Z.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG=Path('D:/work/image/config/image-generation.json')
T='r06_c13';ORIGIN=(49152,20480);N=1254;CORE=1024;H=115
LEFT=['r06_c12_p14-p13-bridge-p14-candidate.png','r06_c12_p24-v2.png','resume-20261010-stall-upper-v1.png','resume-20261010-stall-lower-v1.png']
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):return {'path':str(Path(p).resolve()).replace('\\','/'),'sha256':sha(p),'role':role}
def coords(p):
 r,c=int(p[-2]),int(p[-1]);x=ORIGIN[0]+(c-1)*CORE;y=ORIGIN[1]+(r-1)*CORE;b=[x-H,y-H,x+CORE+H,y+CORE+H]
 return {'id':p,'coreGlobalBox':[x,y,x+CORE,y+CORE],'nativeGlobalBox':b,'overviewBox':[v*1254/57344 for v in b],'expectedSize':[N,N],'nativeCoreBox':[H,H,1139,1139]}
def init():
 refs=[ref(C['layoutReference'],'authoritative layout'),ref(C['detailStyleReference'],'independent materials'),ref(C['primaryStyleReference'],'Q Daoist style')]
 write(Z/'records'/f'{T}.coordinates.json',{'tile':T,'tileOrigin':ORIGIN,'tileCoreBox':[49152,20480,53248,24576],'references':refs,'patches':[coords(f'{T}_p{r}{c}') for r in range(1,5) for c in range(1,5)]})
 layout=Image.open(C['layoutReference']).convert('RGB');box=[1040,412,1190,565];p=Z/'guides'/f'{T}.context-layout-only.png';layout.crop(box).resize((1200,1224),Image.Resampling.NEAREST).save(p)
 write(str(p)+'.derived.json',{'purpose':'wider layout context only; never final pixels','source':ref(C['layoutReference'],'overview'),'sourceBox':box,'operation':'crop and nearest8x only for readability'})
 print(str(p))
def prep(p):
 co=coords(p);im=Image.open(C['layoutReference']).convert('RGB').transform((N,N),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.layout-only.png';im.save(pure)
 choices=json.loads((Z/'records'/f'{T}.working-selection.json').read_text(encoding='utf-8')) if (Z/'records'/f'{T}.working-selection.json').exists() else {}
 r,c=int(p[-2]),int(p[-1]);left=Z/'native'/(LEFT[r-1] if c==1 else choices.get(f'{T}_p{r}{c-1}',f'{T}_p{r}{c-1}-v1.png'));top=Z/'native'/choices.get(f'{T}_p{r-1}{c}',f'{T}_p{r-1}{c}-v1.png') if r>1 else None
 sources=[]
 for path,side in [(left,'left'),(top,'top')]:
  if path:
   a=Image.open(path).convert('RGB');assert a.size==(N,N);box=[1024,0,N,N] if side=='left' else [0,1024,N,N];im.paste(a.crop(box),(0,0));rr=ref(path,'exact_native_'+side+'_230px');rr.update({'cropBox':box,'pasteAt':[0,0]});sources.append(rr)
 gp=Z/'guides'/f'{p}.native-edge-layout.png';im.save(gp);write(str(gp)+'.derived.json',{'purpose':'layout-only with native pixel anchors; not final art','coordinates':co,'sources':[ref(C['layoutReference'],'layout')]+sources,'operation':'EXTENT bicubic layout only plus native opaque1:1 strips; top owns corner'})
 refs=[ref(C['layoutReference'],'full-map layout only'),ref(C['detailStyleReference'],'independent materials only'),ref(C['primaryStyleReference'],'primary style only'),ref(gp,'exact geometry guide plus native edge constraints'),ref(Z/'guides'/f'{T}.context-layout-only.png','wider context layout only')]
 plan={'patchId':p,'createdAtUtc':now(),'coordinates':co,'references':refs,'nativeEdgeSources':sources,'expectedNativeSize':[N,N],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
 plan.update({'configSnapshot':json.loads(CONFIG.read_text(encoding='utf-8-sig')),'configSource':ref(CONFIG,'configured target only, not actual selector'),'configSnapshotCaptureStage':'prepare_before_generation'})
 write(Z/'records'/f'{p}.plan.json',plan);print(json.dumps(plan,ensure_ascii=False))
def ingest(p,src,v):
 pp=Z/'records'/f'{p}-{v}.plan.json'
 if not pp.exists():pp=Z/'records'/f'{p}.plan.json'
 plan=json.loads(pp.read_text(encoding='utf-8'));dst=Z/'native'/f'{p}-{v}.png';assert not dst.exists();shutil.copy2(src,dst);a=Image.open(dst);assert a.size==(N,N)
 prompt=Z/'records'/f'{p}-{v}.prompt.txt';receipt=Z/'records'/f'{p}-{v}.receipt.json';assert prompt.exists() and receipt.exists()
 rr=json.loads(receipt.read_text(encoding='utf-8'));actual=rr.get('request',{}).get('referenced_image_paths');roles={q['path']:q['role'] for q in plan['references']}
 if actual:plan['references']=[ref(x,roles.get(x,'actual submitted reference')) for x in actual]
 record=dict(plan,file=str(dst),sha256=sha(dst),nativeSize=list(a.size),width=a.width,height=a.height,observedAtUtc=now(),prompt=ref(prompt,'actual submitted prompt'),receipt=ref(receipt,'actual tool return receipt'),source=ref(src,'host output byte-for-byte copy'),formalAccepted=False,usable=False,visualReview='pending',status='native_candidate_pending_review',nativeResizePerformed=False)
 write(str(dst)+'.generation.json',record)
 qa=[]
 for e in plan['nativeEdgeSources']:
  b=Image.open(e['path']).convert('RGB');top='top' in e['role'];bottom='bottom' in e['role'];q=Image.new('RGB',(N,256) if top or bottom else (256,N))
  if top:q.paste(b.crop((0,1011,N,1139)),(0,0));q.paste(a.crop((0,115,N,243)),(0,128))
  elif bottom:q.paste(a.crop((0,1011,N,1139)),(0,0));q.paste(b.crop((0,115,N,243)),(0,128))
  elif 'right' in e['role']:q.paste(a.crop((1011,0,1139,N)),(0,0));q.paste(b.crop((115,0,243,N)),(128,0))
  else:q.paste(b.crop((1011,0,1139,N)),(0,0));q.paste(a.crop((115,0,243,N)),(128,0))
  qp=Z/'qa'/f'{p}-{v}-{e["role"]}.png';q.save(qp);qa.append(str(qp));write(str(qp)+'.derived.json',{'purpose':'native1:1 seam QA','sources':[e,ref(dst,'new native')],'seam':128,'resized':False})
 print(json.dumps({'saved':str(dst),'sha256':sha(dst),'nativeSize':list(a.size),'qa':qa}))
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('op');q.add_argument('patch',nargs='?');q.add_argument('--source');q.add_argument('--version',default='v1');a=q.parse_args()
 if a.op=='init':init()
 elif a.op=='prepare':prep(a.patch)
 elif a.op=='ingest':ingest(a.patch,a.source,a.version)
