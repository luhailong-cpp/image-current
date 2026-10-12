from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib,shutil,importlib.util,argparse
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;Z=D.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,j):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
IDS={'r08_c13':{'sha':'7beaf9df09ab9802272b0a78ed75584d437a0b8880ffa21e420e83d1403c934b','fn':'compose','origin':[3469,-627],'crop':[0,627,627,1254],'paste':[3469,0]},'r08_c14':{'sha':'de6180ca265a68efd454404fda86939a951475483868d773ed4b11dd64c094a0','fn':'replay','origin':[-627,-627],'crop':[627,627,1254,1254],'paste':[0,0]}}
POLY=[(530,627),(1190,627),(1190,795),(1130,865),(720,890),(585,830),(530,740)]
def stage():
 r=read(D/'receipts/m01.receipt.json');src=D/'source/m01.png';src.parent.mkdir(exist_ok=True)
 if not src.exists():shutil.copy2(r['sourceOutputPath'],src)
 assert sha(src)==sha(r['sourceOutputPath']);im=Image.open(src).convert('RGB');assert im.size==(1254,1254)
 req=read(D/'prompts/m01.request.json');assert (D/'prompts/m01.prompt.txt').read_text(encoding='utf-8').strip()==req['prompt']
 refs=[{'file':f,'sha256':sha(f)} for f in req['referenced_image_paths']]
 save(str(src)+'.generation.json',{'file':str(src),'sha256':sha(src),'sourceOutputPath':r['sourceOutputPath'],'nativeSize':[1254,1254],'tool':'image_gen','route':'builtin','prompt':str(D/'prompts/m01.prompt.txt'),'request':str(D/'prompts/m01.request.json'),'evidence':str(D/'receipts/m01.receipt.json'),'references':refs,'actualModel':None,'actualQuality':None,'resized':False})
 mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(POLY,fill=255);mask.save(D/'mask.png')
 records={}
 for tid,o in IDS.items():
  T=Z/tid;prior=T/'qa/finish-20261011/apply.py'
  spec=importlib.util.spec_from_file_location(tid+'_prior',prior);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  before,pr=getattr(m,o['fn'])(False)
  archive=D/'before'/f'{tid}.png'
  if archive.exists():assert sha(archive)==o['sha'];assert ImageChops.difference(before,Image.open(archive).convert('RGB')).getbbox() is None
  else:
   current=T/f'candidates/{tid}.candidate.png';assert sha(current)==o['sha'];assert ImageChops.difference(before,Image.open(current).convert('RGB')).getbbox() is None
  canvas=before.copy();part=mask.crop(o['crop']);canvas.paste(im.crop(o['crop']),tuple(o['paste']),part)
  support=Image.new('L',(4096,4096));support.paste(part,tuple(o['paste']));diff=ImageChops.difference(before,canvas);outside=diff.copy();outside.paste((0,0,0),(0,0),support);assert outside.getbbox() is None
  out=D/'staged'/f'{tid}.png';out.parent.mkdir(exist_ok=True);canvas.save(out)
  records[tid]={'priorReplay':str(prior),'priorReplaySha256':sha(prior),'priorCandidateSha256':o['sha'],'staged':str(out),'sha256':sha(out),'sourceCrop':o['crop'],'paste':o['paste'],'changedPixelBox':diff.getbbox(),'nativeCoreCount':16,'priorRepairCount':len(pr['operations']),'outsideMaskPixelIdentical':True}
 preview=Image.open(req['referenced_image_paths'][0]).convert('RGB');preview.paste(im,(0,0),mask);preview.save(D/'integrated-central-100pct.png')
 save(D/'staged.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'tiles':records,'source':str(src),'sourceSha256':sha(src),'mask':str(D/'mask.png'),'maskSha256':sha(D/'mask.png'),'polygon':POLY,'binaryMask':True,'resized':False,'northernTilesUnchanged':True,'formalAcceptedCount':0})
 return records
def main(mode):
 recs=stage()
 if mode=='stage':print(json.dumps(recs));return
 for tid,r in recs.items():
  T=Z/tid;C=T/f'candidates/{tid}.candidate.png';staged=Path(r['staged'])
  if mode=='check':
   assert sha(C)==r['sha256'];assert ImageChops.difference(Image.open(C).convert('RGB'),Image.open(staged).convert('RGB')).getbbox() is None
   continue
  assert sha(C)==r['priorCandidateSha256'];backup=D/'before'/f'{tid}.png';backup.parent.mkdir(exist_ok=True);assert not backup.exists();shutil.copy2(C,backup);shutil.copy2(str(C)+'.generation.json',str(backup)+'.generation.json')
  shutil.copy2(staged,C)
  side=read(str(backup)+'.generation.json');side.update({'sha256':sha(C),'recipe':str(D/'staged.json'),'sourceReplay':str(Path(__file__)),'repairLayerCount':r['priorRepairCount']+1,'visualReview':'central-foliage local verification pending','assetRole':'complete4kCandidate; central shared repair pending local review'});save(str(C)+'.generation.json',side)
  p=read(T/'tile-progress.json');p.update({'candidateSha256':sha(C),'internalPassed4kCount':0,'status':'complete_candidate_central_shared_repair_review_pending'});save(T/'tile-progress.json',p)
 if mode=='check':save(D/'verification.json',{'pixelReplayIdentical':True,'sourceBytesVerified':True,'nativeCoreCountPerTile':16,'outsideMaskPixelIdentical':True,'northernTilesUnchanged':True,'candidates':{tid:r['sha256'] for tid,r in recs.items()}})
 print(json.dumps({'mode':mode,'candidates':{tid:r['sha256'] for tid,r in recs.items()}}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['stage','apply','check']);main(p.parse_args().mode)

