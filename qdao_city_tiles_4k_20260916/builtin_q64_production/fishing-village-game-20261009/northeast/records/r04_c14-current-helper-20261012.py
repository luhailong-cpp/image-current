import argparse,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageOps
Z=Path(__file__).resolve().parent.parent
C=json.loads((Z.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG=Path('D:/work/image/config/image-generation.json')
T='r04_c14';ORIGIN=(53248,12288);N=1254;CORE=1024;H=115
SOUTH=['r05_c14_p11-v3.png','r05_c14_p12-v1.png','r05_c14_p13-v4.png','r05_c14_p14-v2.png']
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8-sig')
def ref(p,role):return {'path':str(Path(p).resolve()).replace('\\','/'),'sha256':sha(p),'role':role}
def coords(p):
 r,c=int(p[-2]),int(p[-1]);x=ORIGIN[0]+(c-1)*CORE;y=ORIGIN[1]+(r-1)*CORE;b=[x-H,y-H,x+CORE+H,y+CORE+H]
 return {'id':p,'coreGlobalBox':[x,y,x+CORE,y+CORE],'nativeGlobalBox':b,'overviewBox':[v*1254/57344 for v in b],'expectedSize':[N,N],'nativeCoreBox':[H,H,1139,1139]}
def init():
 refs=[ref(C['layoutReference'],'authoritative layout'),ref(C['detailStyleReference'],'independent materials'),ref(C['primaryStyleReference'],'Q Daoist style')]
 write(Z/'records'/f'{T}.coordinates.json',{'tile':T,'tileOrigin':ORIGIN,'tileCoreBox':[53248,12288,57344,16384],'references':refs,'patches':[coords(f'{T}_p{r}{c}') for r in range(1,5) for c in range(1,5)]})
 layout=Image.open(C['layoutReference']).convert('RGB');box=[1100,240,1254,367];p=Z/'guides'/f'{T}.context-layout-only.png';layout.crop(box).resize((1232,1016),Image.Resampling.NEAREST).save(p)
 write(str(p)+'.derived.json',{'purpose':'wider layout context only; never final pixels','source':ref(C['layoutReference'],'overview'),'sourceBox':box,'operation':'crop and nearest8x only for readability'})
 print(str(p))
def prep(p):
 co=coords(p);layout=Image.open(C['layoutReference']).convert('RGB');pad=Image.new('RGB',(layout.width+8,layout.height));pad.paste(layout,(0,0));pad.paste(layout.crop((layout.width-1,0,layout.width,layout.height)).resize((8,layout.height)),(layout.width,0));im=pad.transform((N,N),Image.Transform.EXTENT,co['overviewBox'],Image.Resampling.BICUBIC)
 pure=Z/'guides'/f'{p}.layout-only.png';im.save(pure)
 choices=json.loads((Z/'records'/f'{T}.working-selection.json').read_text(encoding='utf-8-sig')) if (Z/'records'/f'{T}.working-selection.json').exists() else {}
 r,c=int(p[-2]),int(p[-1]);left=Z/'native'/choices.get(f'{T}_p{r}{c-1}',f'{T}_p{r}{c-1}-v1.png') if c>1 else None
 if c==1:
  neighborSelection=Z/'records'/'r04_c13.working-selection.json'; nchoices=json.loads(neighborSelection.read_text(encoding='utf-8-sig')) if neighborSelection.exists() else {}; possibleLeft=Z/'native'/nchoices.get(f'r04_c13_p{r}4',f'r04_c13_p{r}4-v1.png'); left=possibleLeft if possibleLeft.exists() else None
 bottom=Z/'native'/(SOUTH[c-1] if r==4 else choices.get(f'{T}_p{r+1}{c}',f'{T}_p{r+1}{c}-v1.png'))
 sources=[]
 for path,side in [(bottom,'bottom'),(left,'left')]:
  if path:
   a=Image.open(path).convert('RGB');assert a.size==(N,N);box=[1024,0,N,N] if side=='left' else [0,0,N,230];at=[0,0] if side=='left' else [0,1024];im.paste(a.crop(box),at);rr=ref(path,'exact_native_'+side+'_230px');rr.update({'cropBox':box,'pasteAt':at});sources.append(rr)
 gp=Z/'guides'/f'{p}.native-edge-layout.png';im.save(gp);write(str(gp)+'.derived.json',{'purpose':'layout-only with native pixel anchors; not final art','coordinates':co,'sources':[ref(C['layoutReference'],'layout')]+sources,'operation':'EXTENT bicubic layout only plus native opaque1:1 strips; left owns corner'})
 refs=[ref(C['layoutReference'],'full-map layout only'),ref(C['detailStyleReference'],'independent materials only'),ref(C['primaryStyleReference'],'primary style only'),ref(gp,'exact geometry guide plus native edge constraints')]
 plan={'patchId':p,'createdAtUtc':now(),'coordinates':co,'references':refs,'nativeEdgeSources':sources,'pendingExternalBoundary':'west neighbor r04_c13 missing' if c==1 and left is None else None,'southAnchorSelectionEvidence':'r05_c14.selection-proposed-v4.json plus r04_c14.south-anchors-pinned.json','expectedNativeSize':[N,N],'tool':'image_gen.imagegen','route':'builtin','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
 plan.update({'configSnapshot':json.loads(CONFIG.read_text(encoding='utf-8-sig')) if CONFIG.exists() else None,'configSource':ref(CONFIG,'configured target only, not actual selector') if CONFIG.exists() else {'path':str(CONFIG),'available':False},'configSnapshotCaptureStage':'prepare_before_generation'})
 write(Z/'records'/f'{p}.plan.json',plan);print(json.dumps(plan,ensure_ascii=False))
def ingest(p,src,v):
 pp=Z/'records'/f'{p}-{v}.plan.json'
 if not pp.exists():pp=Z/'records'/f'{p}.plan.json'
 plan=json.loads(pp.read_text(encoding='utf-8-sig'));dst=Z/'native'/f'{p}-{v}.png';assert not dst.exists();shutil.copy2(src,dst);a=Image.open(dst);assert a.size==(N,N)
 prompt=Z/'records'/f'{p}-{v}.prompt.txt';receipt=Z/'records'/f'{p}-{v}.receipt.json';assert prompt.exists() and receipt.exists()
 rr=json.loads(receipt.read_text(encoding='utf-8-sig'));actual=rr.get('request',{}).get('referenced_image_paths');roles={q['path']:q['role'] for q in plan['references']}
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
