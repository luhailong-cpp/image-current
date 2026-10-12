"""Strict replay of sixteen immutable native cores plus two integer binary-mask repairs."""
from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import json,hashlib,importlib.util,argparse
D=Path(__file__).resolve().parent;T=D.parents[1];Z=T.parent
A=T/'qa/core-baseline/df217b3c44d2eb2195d0/assembly.json'
B=A.parent/'r08_c13-core-baseline.candidate.png'
C=T/'candidates/r08_c13.candidate.png'
NAMES=['road-junction-v1','stone-cut-v1']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def evidence(p):return {'file':str(p),'sha256':sha(p)}
def compose(ingest=False):
 spec=importlib.util.spec_from_file_location('strict_native_assembly',Z/'assemble.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 tile,plan=m.load_plan(T.name);sources,ev,missing,invalid=m.inspect_sources(tile,plan)
 assert len(sources)==16 and not missing and not invalid
 canvas=m.compose(plan,sources).convert('RGB');base=Image.open(B).convert('RGB')
 assert canvas.size==(4096,4096) and ImageChops.difference(canvas,base).getbbox() is None
 ops=[];union=Image.new('L',canvas.size)
 for name in NAMES:
  recordpath=D/'records'/(name+'.json');r=read(recordpath)
  src=Path(r['sourceFile']);maskp=Path(r['mask']);mp=Image.open(maskp).convert('L')
  assert sha(src)==r['sourceSha256']==sha(r['toolOutput'])==r['toolOutputSha256']
  assert sha(maskp)==r['maskSha256'] and set(mp.tobytes())=={0,255}
  im=Image.open(src);assert im.size==(1254,1254) and im.format=='PNG' and ('A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255))
  req=read(r['request']);prompt=Path(r['prompt']).read_text(encoding='utf8')
  if 'prompt' in req:assert req['prompt']==prompt.strip()
  else:assert Path(req['promptFile']).resolve()==Path(r['prompt']).resolve()
  receipt=read(r['receipt']);assert str(r['toolOutput']).replace('/','\\') in receipt['output_hint']
  refs=[evidence(p) for p in req['referenced_image_paths']]
  ctx=read(r['contextRecord']);assert sha(ctx.get('context',req['referenced_image_paths'][0]))==refs[0]['sha256']
  gen={'file':str(src),'sha256':sha(src),'tool':'image_gen','route':'builtin','sourceOutputPath':r['toolOutput'],'nativeSize':[1254,1254],'actualModel':None,'actualQuality':None,'references':refs,'prompt':evidence(r['prompt']),'request':evidence(r['request']),'receipt':evidence(r['receipt']),'resized':False}
  gp=Path(str(src)+'.generation.json')
  if ingest:save(gp,gen)
  else:assert read(gp)==gen
  dest=tuple(r['dest']);canvas.paste(im.convert('RGB'),dest,mp);union.paste(255,(*dest,dest[0]+1254,dest[1]+1254),mp)
  ops.append({'record':evidence(recordpath),'source':evidence(src),'generationRecord':evidence(gp),'mask':evidence(maskp),'sourceCrop':[0,0,1254,1254],'destinationTileXY':list(dest),'tileBox':r['tileBox'],'binaryMask':True,'resized':False})
 diff=ImageChops.difference(canvas,base);outside=diff.copy();outside.paste((0,0,0),(0,0),union);assert outside.getbbox() is None
 for box in [(0,0,4096,192),(0,3904,4096,4096),(0,0,192,4096),(3904,0,4096,4096)]:
  assert ImageChops.difference(base.crop(box),canvas.crop(box)).getbbox() is None
 return canvas,{'baseline':evidence(B),'assembly':evidence(A),'nativeCoreCount':16,'nativeSourceEvidence':ev,'operations':ops,'outsideMasksPixelIdentical':True,'outer192pxPixelIdentical':True,'changedPixelBox':diff.getbbox(),'resized':False,'warped':False,'blurred':False,'feathered':False,'formalAcceptedCount':0}
def main(check=False):
 canvas,rec=compose(not check)
 if check:
  old=read(D/'replay.json');assert sha(C)==old['outputSha256'];assert ImageChops.difference(canvas,Image.open(C).convert('RGB')).getbbox() is None
  proof={'candidate':str(C),'candidateSha256':sha(C),'nativeCoreCount':16,'repairLayerCount':2,'pixelReplayIdentical':True,'sourceBytesVerified':True,'outsideMasksPixelIdentical':True,'outer192pxPixelIdentical':True,'formalAcceptedCount':0}
  save(D/'verification.json',proof);print(json.dumps(proof));return
 assert not C.exists(),'Candidate already exists; use --check'
 C.parent.mkdir(exist_ok=True);canvas.save(C)
 rec.update({'output':str(C),'outputSha256':sha(C),'createdAt':datetime.now(timezone.utc).isoformat()});save(D/'replay.json',rec)
 save(str(C)+'.generation.json',{'file':str(C),'sha256':sha(C),'width':4096,'height':4096,'format':'PNG','assetRole':'complete4kCandidate; visual review awaiting final evidence','derivedFrom':[evidence(B)],'operation':{'method':'sixteen1254-native1024core integer crops, then two builtin-native binary-mask repairs','resized':False,'feathered':False},'actualModel':None,'actualQuality':None,'formalAcceptedCount':0,'recipe':str(D/'replay.json'),'sourceReplay':str(Path(__file__)),'repairLayerCount':2})
 # Export candidate versions of all native pair and intersection windows.
 out=D/'review/final-windows';out.mkdir(exist_ok=True)
 manifest=read(A);wins=[]
 for item in manifest['artifacts']:
  p=Path(item['file'])
  if p.name.startswith(('vertical-','horizontal-','intersection-')) and p.name.endswith('-100pct.png') and 'join' in p.name or p.name.startswith('intersection-'):
   box=item.get('crop')
   if box is None:continue
   im=canvas.crop(tuple(box));fp=out/p.name;im.save(fp)
   original=Image.open(p).convert('RGB')
   wins.append({'file':str(fp),'sha256':sha(fp),'tileBox':box,'baselineFile':str(p),'baselineSha256':sha(p),'pixelIdenticalToReviewedBaseline':ImageChops.difference(im,original).getbbox() is None})
 save(D/'review/final-window-manifest.json',wins)
 # Final candidate north windows must exactly equal already reviewed native-source windows.
 north=Z/'r07_c13/candidates/r07_c13.candidate.png';ni=Image.open(north).convert('RGB');northwins=[]
 for c in range(1,5):
  x=(c-1)*1024;im=Image.new('RGB',(1024,384));im.paste(ni.crop((x,3904,x+1024,4096)),(0,0));im.paste(canvas.crop((x,0,x+1024,192)),(0,192))
  old=T/'qa/north-review'/f'north-c{c}-1to1.png'
  assert ImageChops.difference(im,Image.open(old).convert('RGB')).getbbox() is None
  fp=D/'review'/f'final-north-c{c}-100pct.png';im.save(fp)
  northwins.append({'file':str(fp),'sha256':sha(fp),'northCandidate':evidence(north),'southCandidate':evidence(C),'reviewedNativeWindow':evidence(old),'pixelsIdenticalToReviewedNativeWindow':True,'visualStatus':'passed; no P2 structural mismatch'})
 save(D/'review/north-final-review.json',{'windows':northwins,'count':4,'sourceWindowInspection':'All four original-resolution native-source windows visually reviewed; final candidate windows proven pixel identical.','formalAcceptedCount':0})
 print(json.dumps({'candidateSha256':sha(C),'windowCount':len(wins),'unchangedWindows':sum(w['pixelIdenticalToReviewedBaseline'] for w in wins),'northWindowsIdentical':4}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');main(p.parse_args().check)

