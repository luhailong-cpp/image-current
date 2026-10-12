from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import json, hashlib, shutil, sys

ROOT=Path(__file__).resolve().parent
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
TILES=['r03_c10','r03_c11','r04_c10','r04_c11']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def boxes(t,sr,sc):
 assert t in TILES
 r,c=int(t[1:3]),int(t[5:7]);x=(c-1)*4096+(sc-1)*1024;y=(r-1)*4096+(sr-1)*1024
 return [x,y,x+1024,y+1024],[x-115,y-115,x+1139,y+1139]
def refs():return [{'file':CONTRACT[k],'sha256':sha(CONTRACT[k]),'role':role} for k,role in [('layoutReference','approved geometry only'),('detailStyleReference','approved materials and daylight only; not coordinate geometry'),('primaryStyleReference','rounded Q Daoist art only; no UI/characters/night')]]
def setup():
 for t in TILES:
  for d in ['guides','native','records','qa','candidate']:(ROOT/t/d).mkdir(parents=True,exist_ok=True)
 im=Image.open(CONTRACT['layoutReference'])
 region=[36864,8192,45056,16384]
 im.transform((1254,1254),Image.Transform.EXTENT,[v*1254/57344 for v in region],Image.Resampling.NEAREST).save(ROOT/'region-layout-only.png')
 write(ROOT/'coordinate-plan.json',{'tiles':TILES,'globalPixelBox':region,'referenceMapping':'1254 overview to 57344 map, layout only','nativeCorePixels':1024,'haloPixels':115,'expectedNativePixels':1254,'references':refs(),'formalAcceptedCount':0,'hasDirectExternalNativeBoundary':False})
 update()
def update():
 completed=[];nextp=None;tiles={}
 for t in TILES:
  arr=[]
  for r in range(1,5):
   for c in range(1,5):
    p=ROOT/t/'records'/f'p{r}{c}.selection.json'
    if p.exists():arr.append(f'p{r}{c}');completed.append(t+':'+f'p{r}{c}')
    elif nextp is None:nextp={'tile':t,'patch':f'p{r}{c}'}
  tiles[t]={'nativeCoresSelected':len(arr),'selected':arr,'formalAccepted':False}
 write(ROOT/'progress.json',{'updatedAt':now(),'status':'native_generation_in_progress','tiles':tiles,'selectedNativeCoreCount':len(completed),'requiredNativeCoreCount':64,'nextCoordinate':nextp,'formalAcceptedCount':0,'builtinOnly':True,'paidApiUsed':False,'actualModel':None,'actualQuality':None,'externalSeamsChecked':False})
def prepare(t,sr,sc,v=1):
 core,box=boxes(t,sr,sc);name=f'p{sr}{sc}-v{v}';dest=ROOT/t;source=CONTRACT['layoutReference']
 im=Image.open(source).transform((1254,1254),Image.Transform.EXTENT,[z*1254/57344 for z in box],Image.Resampling.BICUBIC).convert('RGB')
 ns=[]
 for other in TILES:
  for p in (ROOT/other/'records').glob('p??.selection.json'):
   sel=read(p);g=read(sel['generationRecord']);bb=g['globalNativeBox']
   if sel['file']==str(dest/'native'/f'{name}.png'):continue
   inter=[max(box[0],bb[0]),max(box[1],bb[1]),min(box[2],bb[2]),min(box[3],bb[3])]
   if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
   crop=[inter[0]-bb[0],inter[1]-bb[1],inter[2]-bb[0],inter[3]-bb[1]];at=[inter[0]-box[0],inter[1]-box[1]]
   im.paste(Image.open(sel['file']).crop(crop),at);ns.append({'file':sel['file'],'sha256':sha(sel['file']),'sourceCrop':crop,'pasteAt':at,'role':'exact unscaled adjacent native overlap'})
 guide=dest/'guides'/f'{name}-positional.png';im.save(guide)
 write(guide.with_suffix('.derivation.json'),{'globalCoreBox':core,'globalNativeBox':box,'overviewSource':source,'overviewSha256':sha(source),'nativeOverlaps':ns,'classification':'layout guide with native context, never final artwork','nativePixelsResized':False})
 print(json.dumps({'file':str(guide),'core':core,'native':box,'nativeContextCount':len(ns)}))
def record(t,sr,sc,v,src):
 name=f'p{sr}{sc}-v{v}';dest=ROOT/t;p=dest/'native'/f'{name}.png';assert not p.exists();shutil.copy2(src,p);im=Image.open(p);core,box=boxes(t,sr,sc)
 request=read(dest/'records'/f'{name}.request.json');receipt=read(dest/'records'/f'{name}.receipt.json')
 record={'file':str(p),'sha256':sha(p),'nativeDimensions':list(im.size),'format':im.format,'globalCoreBox':core,'globalNativeBox':box,'coreCropNative':[115,115,1139,1139],'nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Built-in tool does not expose model or quality selectors or verified model metadata','sourcePath':src,'prompt':request['prompt'],'promptFile':str(dest/'records'/f'{name}.prompt.txt'),'references':[{'file':q,'sha256':sha(q),'role':request['referenceRoles'][i]} for i,q in enumerate(request['referenced_image_paths'])],'receipt':receipt,'status':'candidate_pending_geometry_and_seam_review','recordedAt':now()}
 g=p.with_suffix('.generation.json');write(g,record)
 if im.size!=(1254,1254):raise RuntimeError('Unexpected native size; do not resize. Replan native coverage.')
 write(dest/'records'/f'p{sr}{sc}.selection.json',{'file':str(p),'sha256':sha(p),'generationRecord':str(g),'status':'candidate_pending_seam_QA'})
 update();print(json.dumps({'file':str(p),'nativeDimensions':list(im.size),'sha256':sha(p)}))
def assemble(t):
 im=Image.new('RGB',(4096,4096));sources=[]
 for r in range(1,5):
  for c in range(1,5):
   q=read(ROOT/t/'records'/f'p{r}{c}.selection.json');s=Image.open(q['file']);assert s.size==(1254,1254)
   im.paste(s.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));sources.append(q)
 out=ROOT/t/'candidate'/f'{t}-4096-candidate-v1.png';im.save(out)
 write(out.with_suffix('.manifest.json'),{'file':str(out),'sha256':sha(out),'dimensions':[4096,4096],'sources':sources,'operation':'16 native 1024 square core pixel crops; no resampling','formalAccepted':False,'seamReview':'pending'})
 preview=im.copy();preview.thumbnail((1024,1024));preview.save(ROOT/t/'qa'/'candidate-preview.png')
 for a in [1024,2048,3072]:
  for b in range(4):
   im.crop((a-128,b*1024,a+128,(b+1)*1024)).save(ROOT/t/'qa'/f'vertical-x{a}-y{b*1024}.png')
   im.crop((b*1024,a-128,(b+1)*1024,a+128)).save(ROOT/t/'qa'/f'horizontal-y{a}-x{b*1024}.png')
 print(json.dumps({'candidate':str(out),'nativeSeamCrops':24}))
if __name__=='__main__':
 a=sys.argv
 if a[1]=='setup':setup()
 elif a[1]=='prepare':prepare(a[2],*map(int,a[3:]))
 elif a[1]=='record':record(a[2],*map(int,a[3:6]),a[6])
 elif a[1]=='assemble':assemble(a[2])
 elif a[1]=='update':update()
