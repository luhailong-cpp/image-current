from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
from datetime import datetime,timezone
import hashlib,json,shutil,importlib.util,argparse
D=Path(__file__).resolve().parent;T=D.parents[1];Z=T.parent
A=T/'qa/core-baseline/a08b236df6a6c9ae8a1d/assembly.json';B=A.parent/'r08_c14-core-baseline.candidate.png'
C=T/'candidates/r08_c14.candidate.png'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PLANS=[('m01-stone',[397,2143],[(140,745),(635,525),(810,565),(835,690),(225,880),(140,865)])]
def replay(ingest=False):
 spec=importlib.util.spec_from_file_location('verified_native_assembly',Z/'assemble.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 tile,plan=m.load_plan(T.name);native,evidence,missing,invalid=m.inspect_sources(tile,plan);assert len(native)==16 and not missing and not invalid
 canvas=m.compose(plan,native).convert('RGB');base=Image.open(B).convert('RGB');assert ImageChops.difference(canvas,base).getbbox() is None
 ops=[];union=Image.new('L',(4096,4096))
 for name,dest,polygon in PLANS:
  r=read(D/'prompts'/(name+'.request.json'));receipt=read(D/'receipts'/(name+'.receipt.json'))
  src=D/'source'/(name+'.png');src.parent.mkdir(exist_ok=True)
  toolsource=Path(receipt['sourceOutputPath'])
  if ingest and not src.exists():shutil.copy2(toolsource,src)
  assert sha(src)==sha(toolsource)
  with Image.open(src) as im:assert im.size==(1254,1254) and im.format=='PNG';art=im.convert('RGB')
  refs=[{'file':f,'sha256':sha(f)} for f in r['referenced_image_paths']]
  prompt=D/'prompts'/(name+'.prompt.txt');assert prompt.read_text(encoding='utf-8').strip()==r['prompt']
  record={'file':str(src),'sha256':sha(src),'sourceOutputPath':str(toolsource),'nativeSize':[1254,1254],'format':'PNG','tool':'image_gen','route':'builtin','actualModel':None,'actualQuality':None,'prompt':str(prompt),'request':str(D/'prompts'/(name+'.request.json')),'evidence':str(D/'receipts'/(name+'.receipt.json')),'references':refs,'resized':False}
  if ingest:save(Path(str(src)+'.generation.json'),record)
  else:
   old=read(Path(str(src)+'.generation.json'));assert old['sha256']==record['sha256'];assert old['references']==refs
  mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(polygon,fill=255)
  mp=D/'masks'/(name+'.png')
  if ingest:mp.parent.mkdir(exist_ok=True);mask.save(mp)
  else:assert ImageChops.difference(mask,Image.open(mp)).getbbox() is None
  canvas.paste(art,tuple(dest),mask);union.paste(255,(dest[0],dest[1],dest[0]+1254,dest[1]+1254),mask)
  ops.append({'source':str(src),'sourceSha256':sha(src),'generationRecord':str(src)+'.generation.json','generationRecordSha256':sha(str(src)+'.generation.json'),'mask':str(mp),'maskSha256':sha(mp),'destinationTileXY':dest,'sourceCrop':[0,0,1254,1254],'binaryMask':True,'polygon':polygon,'resized':False})
  if ingest:canvas.crop([dest[0],dest[1],dest[0]+1254,dest[1]+1254]).save(D/(name+'-integrated-100pct.png'))
 diff=ImageChops.difference(base,canvas);outside=diff.copy();outside.paste((0,0,0),(0,0),union);assert outside.getbbox() is None
 return canvas,{'baseline':str(B),'baselineSha256':sha(B),'assembly':str(A),'assemblySha256':sha(A),'nativeSourcesVerified':16,'operations':ops,'outsideMasksPixelIdentical':True,'changedPixelBox':diff.getbbox(),'resized':False,'warped':False,'blurred':False,'feathered':False,'formalAcceptedCount':0}
def main(check):
 canvas,record=replay(not check)
 if check:
  saved=read(D/'replay.json');assert sha(C)==saved['outputSha256'];assert ImageChops.difference(canvas,Image.open(C).convert('RGB')).getbbox() is None
  save(D/'verification.json',{'pixelReplayIdentical':True,'sourceBytesVerified':True,'outsideMasksPixelIdentical':True,'repairLayerCount':len(record['operations']),'nativeCoreCount':16,'candidateSha256':sha(C)});print(json.dumps({'pixelReplayIdentical':True,'sha256':sha(C)}));return
 assert sha(C)=='522091916baa3c1bea6191dfc9dfe718d5ba3dc0aea278aef11a8ab08e4d36de','Refuse unexpected candidate'
 shutil.copy2(C,D/'before.candidate.png');shutil.copy2(str(C)+'.generation.json',D/'before.generation.json')
 canvas.save(C);record.update({'output':str(C),'outputSha256':sha(C),'createdAt':datetime.now(timezone.utc).isoformat(),'visualReview':'pending'});save(D/'replay.json',record)
 side=read(D/'before.generation.json');side.update({'sha256':sha(C),'recipe':str(D/'replay.json'),'sourceReplay':str(Path(__file__)),'repairLayerCount':len(PLANS),'operation':{'method':'16 verified native core crops and bounded native repair masks','resized':False,'feathered':False},'assetRole':'complete4kCandidate; local repair applied; visual review pending'});save(Path(str(C)+'.generation.json'),side)
 progress=read(T/'tile-progress.json');progress.update({'candidateSha256':sha(C),'nativeCount':17,'selectedRepairCount':1,'status':'complete_4k_candidate_local_repair_applied_review_pending','nextStep':'Review final repair and remaining internal seams; external group review pending'});save(T/'tile-progress.json',progress)
 print(json.dumps({'candidateSha256':sha(C),'layers':len(PLANS),'outsideMasksPixelIdentical':True,'changedPixelBox':record['changedPixelBox']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)

