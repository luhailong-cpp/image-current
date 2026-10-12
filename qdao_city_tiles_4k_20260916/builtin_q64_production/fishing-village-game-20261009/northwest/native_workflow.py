from pathlib import Path
from PIL import Image
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def boxes(sr,sc):
 x,y=8192+(sc-1)*1024,8192+(sr-1)*1024
 return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def update(**kw):
 p=read(ROOT/'progress.json');p.update(kw);p['updatedAt']=datetime.now(timezone.utc).isoformat();write(ROOT/'progress.json',p)
def prepare(sr,sc):
 ident=f'r03_c03_s{sr:02d}_s{sc:02d}';core,box=boxes(sr,sc)
 ref=Path(CONTRACT['layoutReference']);ob=[v*1254/57344 for v in box]
 guide=Image.open(ref).transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC)
 refs=[{'file':str(ref),'sha256':sha(ref),'role':'layout-only global map'}];neighbors=[]
 for pr,pc in [(sr,sc-1),(sr-1,sc),(sr,sc+1),(sr+1,sc)]:
  paths=sorted((ROOT/'native').glob(f'r03_c03_s{pr:02d}_s{pc:02d}_v*.png'))
  if not paths:continue
  p=paths[-1];r=read(Path(str(p)+'.generation.json'));bb=r['globalNativeBox']
  inter=[max(box[0],bb[0]),max(box[1],bb[1]),min(box[2],bb[2]),min(box[3],bb[3])]
  if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
  src=[inter[0]-bb[0],inter[1]-bb[1],inter[2]-bb[0],inter[3]-bb[1]]
  dest=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]]
  guide.paste(Image.open(p).crop(src),tuple(dest[:2]))
  neighbors.append({'file':str(p),'sha256':sha(p),'globalIntersection':inter,'sourceCrop':src,'destinationBox':dest})
  refs.append({'file':str(p),'sha256':sha(p),'role':'exact native overlap pasted into positional guide'})
 path=ROOT/'guides'/f'{ident}.layout-and-native-overlap.png'
 guide.save(path)
 rec={'file':str(path),'sha256':sha(path),'role':'layout-only resampled pixels plus explicitly listed unscaled native overlap; never final art','derivedFrom':refs,'operation':'fractional extent layout crop then exact integer native overlap paste; no feather','globalCoreBox':core,'globalNativeBox':box,'overviewFractionalBox':ob,'nativeCoreCropBox':[115,115,1139,1139],'neighbors':neighbors}
 write(Path(str(path)+'.derivation.json'),rec)
 update(status='preparing-native',currentPatch=f's{sr:02d}_s{sc:02d}',nextStep='Generate next native with overlap pinned; inspect seams at 100%')
 print(json.dumps(rec,ensure_ascii=False))
def record(ident,origin=None):
 receipt=read(ROOT/'receipts'/f'{ident}.receipt.json');req=read(ROOT/'receipts'/f'{ident}.request.json')
 dst=ROOT/'native'/f'{ident}.png';shutil.copy2(receipt['originalFile'],dst)
 im=Image.open(dst);im.load()
 if origin is None:
  sr,sc=int(ident.split('_')[2][1:]),int(ident.split('_')[3][1:])
  core,box=boxes(sr,sc)
 else:
  x,y=origin;box=[x,y,x+1254,y+1254];core=[x+115,y+115,x+1139,y+1139]
 if im.size!=(1254,1254): raise RuntimeError(f'Native size {im.size}: STOP; coverage must be replanned without resize')
 roles=req.get('referenceRoles',['exact positional guide with any neighbor native pixels','tile context only','whole map layout only','independent material detail style only','principal approved painting style only'])
 refs=[{'file':p,'sha256':sha(p),'role':roles[i] if i<len(roles) else 'neighbor native geometry'} for i,p in enumerate(req['referenced_image_paths'])]
 rec={'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(PROJECT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':receipt['unverifiedReason'],'evidence':{'receipt':str(ROOT/'receipts'/f'{ident}.receipt.json'),'fields':['output_hint'],'request':str(ROOT/'receipts'/f'{ident}.request.json')},'prompt':req['promptFile'],'references':refs,'globalCoreBox':core,'globalNativeBox':box,'nativeCoreCropBox':[115,115,1139,1139],'status':'candidate-pending-seam-review','nativeScaleResampled':False}
 write(Path(str(dst)+'.generation.json'),rec)
 p=read(ROOT/'progress.json');p['generatedNativeCount']=len(list((ROOT/'native').glob('*.png')));p['status']='native-generated-pending-QA';p['updatedAt']=datetime.now(timezone.utc).isoformat();write(ROOT/'progress.json',p)
 print(json.dumps({'file':str(dst),'sha256':rec['sha256'],'nativePixels':list(im.size),'generatedNativeCount':p['generatedNativeCount']},ensure_ascii=False))
ap=argparse.ArgumentParser();ap.add_argument('action');ap.add_argument('args',nargs='*');a=ap.parse_args()
if a.action=='prepare':prepare(*map(int,a.args))
elif a.action=='record':record(a.args[0])
elif a.action=='record-repair':record(a.args[0],list(map(int,a.args[1:])))

