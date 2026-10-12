from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
from datetime import datetime,timezone
import hashlib,json,shutil,importlib.util,argparse
D=Path(__file__).resolve().parent;T=D.parents[1];Z=T.parent
A=T/'qa/core-baseline/f30ef04cf1155a6e57a2/assembly.json';B=A.parent/'r07_c13-core-baseline.candidate.png'
C=T/'candidates/r07_c13.candidate.png'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PLANS=[
('m01-plaque',[397,1720],[(118,846),(817,233),(855,315),(825,425),(260,932),(137,916)]),
('m02-eave',[2445,1550],[(350,300),(1090,300),(1090,970),(350,970)]),
('m03-ridge',[1550,1500],[(490,588),(529,597),(551,641),(545,688),(519,719),(490,689)])
]
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
  before=canvas.copy();canvas.paste(art,tuple(dest),mask);union.paste(255,(dest[0],dest[1],dest[0]+1254,dest[1]+1254),mask)
  op={'source':str(src),'sourceSha256':sha(src),'generationRecord':str(src)+'.generation.json','generationRecordSha256':sha(str(src)+'.generation.json'),'mask':str(mp),'maskSha256':sha(mp),'destinationTileXY':dest,'sourceCrop':[0,0,1254,1254],'binaryMask':True,'polygon':polygon,'resized':False}
  ops.append(op)
  if ingest:
   canvas.crop([dest[0],dest[1],dest[0]+1254,dest[1]+1254]).save(D/(name+'-integrated-100pct.png'))
 diff=ImageChops.difference(base,canvas);outside=diff.copy();outside.paste((0,0,0),(0,0),union);assert outside.getbbox() is None
 return canvas,{'baseline':str(B),'baselineSha256':sha(B),'assembly':str(A),'assemblySha256':sha(A),'nativeSourcesVerified':16,'operations':ops,'outsideMasksPixelIdentical':True,'changedPixelBox':diff.getbbox(),'resized':False,'warped':False,'blurred':False,'feathered':False,'formalAcceptedCount':0}
def main(check):
 canvas,record=replay(not check)
 if check:
  saved=read(D/'replay.json');assert sha(C)==saved['outputSha256'];assert ImageChops.difference(canvas,Image.open(C).convert('RGB')).getbbox() is None
  save(D/'verification.json',{'pixelReplayIdentical':True,'sourceBytesVerified':True,'outsideMasksPixelIdentical':True,'repairLayerCount':len(record['operations']),'nativeCoreCount':16,'candidateSha256':sha(C)});print(json.dumps({'pixelReplayIdentical':True,'sha256':sha(C)}));return
 assert sha(C)==sha(B),'Refuse overwrite non-baseline candidate'
 shutil.copy2(C,D/'before.candidate.png');shutil.copy2(str(C)+'.generation.json',D/'before.generation.json')
 canvas.save(C);record.update({'output':str(C),'outputSha256':sha(C),'createdAt':datetime.now(timezone.utc).isoformat(),'visualReview':'pending'});save(D/'replay.json',record)
 side=read(D/'before.generation.json');side.update({'sha256':sha(C),'recipe':str(D/'replay.json'),'sourceReplay':str(Path(__file__)),'repairLayerCount':len(record['operations']),'assetRole':'complete4kCandidate; local repairs applied; visual review pending'});save(Path(str(C)+'.generation.json'),side)
 progress=read(T/'tile-progress.json');progress.update({'candidateSha256':sha(C),'nativeCount':len(list((T/'native').glob('*.png')))+len(PLANS),'selectedRepairCount':len(PLANS),'status':'complete_4k_candidate_local_repairs_applied_review_pending','nextStep':'Review native-size repaired boundaries and all remaining seam windows; internalPassed remains0.'});save(T/'tile-progress.json',progress)
 print(json.dumps({'candidateSha256':sha(C),'layers':len(PLANS),'outsideMasksPixelIdentical':True}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)

