from pathlib import Path
from PIL import Image
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def config_evidence():
 primary=ROOT.parents[3]/'config/image-generation.json'
 recovered=ROOT/'work-r03_c04/resume-20261010/config/image-generation.json'
 p=primary if primary.is_file() else recovered
 return {'snapshot':read(p),'file':str(p),'sha256':sha(p),'recoveredHistoricalBatchSnapshot':p==recovered,'recoveryManifest':str(ROOT/'work-r03_c04/resume-20261010/recovery-manifest.json') if p==recovered else None}
def resolve(p):return Path(p) if Path(p).is_absolute() else ROOT/p
def dims(tile,sr,sc):
 r,c=[int(a[1:]) for a in tile.split('_')]
 x,y=(c-1)*4096+(sc-1)*1024,(r-1)*4096+(sr-1)*1024
 return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def work(tile):
 p=ROOT/f'work-{tile}';p.mkdir(exist_ok=True)
 for d in ['guides','receipts','prompts','qa','tiles']:(p/d).mkdir(exist_ok=True)
 return p
def prepare(tile,sr,sc):
 w=work(tile);core,box=dims(tile,sr,sc)
 candidates=[]
 for plan in [ROOT/'assembly-plan.json',*ROOT.glob('work-*/selected.json'),*ROOT.glob('work-*/selections/*.json')]:
  if not plan.exists():continue
  data=read(plan)
  for s in data.get('sources',[data] if 'file' in data else []):
   p=resolve(s['file'])
   if p.is_file():candidates.append(p)
 ref=Path(CONTRACT['layoutReference']);im=Image.open(ref)
 ob=[v*1254/57344 for v in box]
 guide=im.transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC)
 used=[]
 for p in candidates:
  r=read(str(p)+'.generation.json');b=r['globalNativeBox']
  inter=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
  if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
  # Only adjacent contexts, never overwrite the new patch interior with previous versions.
  rc=r['globalCoreBox']
  if rc[:2]==core[:2]:continue
  src=[inter[0]-b[0],inter[1]-b[1],inter[2]-b[0],inter[3]-b[1]]
  dest=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]]
  guide.paste(Image.open(p).crop(src),tuple(dest[:2]))
  used.append({'file':str(p),'sha256':sha(p),'sourceCrop':src,'destinationBox':dest,'globalIntersection':inter})
 ident=f'{tile}_s{sr:02d}_s{sc:02d}'
 out=w/'guides'/f'{ident}.layout-and-native-overlap.png';guide.save(out)
 write(str(out)+'.derivation.json',{'file':str(out),'sha256':sha(out),'role':'position guide only; resampled layout plus exact unscaled neighbor strips','layout':{'file':str(ref),'sha256':sha(ref)},'globalCoreBox':core,'globalNativeBox':box,'overviewFractionalBox':ob,'neighbors':used,'nativeCoreCropBox':[115,115,1139,1139]})
 r,c=[int(a[1:]) for a in tile.split('_')];tbox=[(c-1)*4096,(r-1)*4096,c*4096,r*4096]
 context=w/'guides'/f'{tile}.layout-only.png'
 if not context.exists():
  tob=[v*1254/57344 for v in tbox]
  im.transform((1254,1254),Image.Transform.EXTENT,tuple(tob),resample=Image.Resampling.BICUBIC).save(context)
  write(str(context)+'.derivation.json',{'file':str(context),'sha256':sha(context),'role':'layout-only guide; never final pixels','source':str(ref),'sourceSha256':sha(ref),'globalBox':tbox,'overviewFractionalBox':tob})
 print(json.dumps({'guide':str(out),'context':str(context),'core':core,'native':box,'neighbors':used},ensure_ascii=False))
def record(tile,ident):
 w=work(tile);rec=read(w/'receipts'/f'{ident}.receipt.json');req=read(w/'receipts'/f'{ident}.request.json')
 dst=ROOT/'native'/f'{ident}.png'
 if dst.exists():raise RuntimeError('Refuse overwrite native')
 shutil.copy2(rec.get('originalFile',rec.get('sourcePath')),dst)
 im=Image.open(dst);im.load()
 if im.size!=(1254,1254):raise RuntimeError(f'STOP unexpected native size {im.size}')
 if 'globalNativeBox' in req and 'globalCoreBox' in req:core,box=req['globalCoreBox'],req['globalNativeBox']
 else:
  sr,sc=int(ident.split('_')[2][1:]),int(ident.split('_')[3][1:]);core,box=dims(tile,sr,sc)
 rr=[{'file':p,'sha256':sha(p),'role':role} for p,role in zip(req['referenced_image_paths'],req['referenceRoles'],strict=True)]
 meta={'file':str(dst),'sha256':sha(dst),'generatedAt':rec.get('returnedAt',datetime.now(timezone.utc).isoformat()),'width':im.width,'height':im.height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config_evidence()['snapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in request has no selectors and response no model/quality metadata. Config is target only.','evidence':{'receipt':str(w/'receipts'/f'{ident}.receipt.json'),'request':str(w/'receipts'/f'{ident}.request.json'),'fields':['output_hint']},'prompt':req['promptFile'],'references':rr,'globalCoreBox':core,'globalNativeBox':box,'nativeCoreCropBox':[115,115,1139,1139],'status':'candidate-pending-seam-review','nativeScaleResampled':False}
 cfg=config_evidence();meta['configSnapshot']=cfg.pop('snapshot');meta['configEvidence']=cfg
 write(str(dst)+'.generation.json',meta)
 print(json.dumps({'file':str(dst),'sha256':sha(dst),'nativePixels':list(im.size)},ensure_ascii=False))
def select(tile,ident):
 w=work(tile);p=ROOT/'native'/f'{ident}.png';rp=Path(str(p)+'.generation.json');r=read(rp)
 sel=read(w/'selected.json') if (w/'selected.json').exists() else {'tile':tile,'sources':[]}
 sr,sc=int(ident.split('_')[2][1:]),int(ident.split('_')[3][1:])
 sel['sources']=[s for s in sel['sources'] if (s['row'],s['column'])!=(sr,sc)]
 sel['sources'].append({'sourceId':(sr-1)*4+sc,'row':sr,'column':sc,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'generationRecord':rp.relative_to(ROOT).as_posix(),'generationRecordSha256':sha(rp),'selectionStatus':'pending-seam-QA'})
 sel['sources'].sort(key=lambda s:s['sourceId']);write(w/'selected.json',sel)
 print(json.dumps({'selected':ident,'count':len(sel['sources'])}))
a=argparse.ArgumentParser();a.add_argument('action');a.add_argument('tile');a.add_argument('args',nargs='*');args=a.parse_args()
if args.action=='prepare':prepare(args.tile,*map(int,args.args))
elif args.action=='record':record(args.tile,args.args[0])
elif args.action=='select':select(args.tile,args.args[0])
