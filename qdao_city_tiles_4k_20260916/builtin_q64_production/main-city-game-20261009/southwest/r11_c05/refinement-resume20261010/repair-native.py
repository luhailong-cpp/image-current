from pathlib import Path
import json,hashlib,argparse,shutil
from datetime import datetime,timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;R=T.parent
for d in ['inputs','prompts','receipts','native','qa']:(D/d).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def evidence(p,role):return {'file':str(p),'sha256':sha(p),'role':role,'pixels':list(Image.open(p).size)}
def prepare(col):
 name=f'p01_{col:02d}';target=T/'native'/f'{name}.png';north=T/'borders'/'r10-south-native-overlap.png'
 seed=Image.open(target).convert('RGB');strip=Image.open(north).crop(((col-1)*1024,0,(col-1)*1024+1254,230)).convert('RGB')
 strip_path=D/'inputs'/f'{name}.north-native-230.png';strip.save(strip_path,optimize=True);neighbors=[]
 if col>1:
  prev=D/'native'/f'p01_{col-1:02d}.png'
  if not prev.exists():prev=T/'native'/f'p01_{col-1:02d}.png'
  left=Image.open(prev).crop((1024,0,1254,1254)).convert('RGB');left_path=D/'inputs'/f'{name}.left-native-230.png';left.save(left_path,optimize=True)
  seed.paste(left,(0,0));seed.paste(Image.open(target).crop((0,1024,1254,1254)),(0,1024))
  neighbors.append(evidence(left_path,'exact left neighbor 230px overlap; color and stair geometry anchor'))
 seed.paste(strip,(0,0));seed_path=D/'inputs'/f'{name}.north-anchored-edit-target.png';seed.save(seed_path,optimize=True)
 c=read(R.parent/'production-contract.json')
 refs=[evidence(seed_path,'1254x1254 EDIT TARGET: original native with exact top and optional left neighbor bands placed'),evidence(strip_path,'exact top 230px native r10 border at identical pixel scale')]
 refs += [evidence(Path(c['layoutReference']),'approved city layout: context only, never widen crop'),evidence(Path(c['detailStyleReference']),'approved natural stone material and daylight'),evidence(Path(c['primaryStyleReference']),'approved rounded Daoist style; never copy UI')]
 features='Preserve every green leaf silhouette and stem, red banner and gold rings, stone parapet and ball finial exactly.' if col==1 else 'The crop contains ONLY broad nearly horizontal stone stairs. Preserve every tread, riser, highlight and grout edge in its original position. No vertical joints or added slabs.'
 prompt=f'''Use case: precise-object-edit. Asset: native game-art patch {name}.
Edit IMAGE 1 only. Return exactly ONE opaque square PNG, native 1254 x 1254 pixels, with IDENTICAL framing and geometry. This is subtle material continuity correction of a tiny extreme-close crop, not a new scene.
Image 1 contains the exact neighboring top 230 pixel band. Image 2 shows that native top band separately as the shape/color anchor. {'The left 230 pixel band in image 1 is copied from the actual left neighbor.' if col>1 else ''} The last three images are approved whole-city layout, stone material and Daoist style references only; never copy their composition.
Fix only discontinuous warm/cool stone shading and overly cellular or marbled texture in image 1 interior. Stone color must continue naturally from the authentic top band and {'left overlap' if col>1 else 'surrounding approved stone'}. Broad smooth pale grey / soft grey-beige planes, very faint brush texture. No polygon patches of different colors, flakes, dense scales or heavy veins. Preserve the existing light and shadow shapes.
LOCK the entire top band y=0..229 exactly as image 1 / image 2. LOCK the bottom band y=1024..1253 exactly as image 1 because it is connected to another patch. {'LOCK left x=0..229 except corners follow image 1.' if col>1 else ''} Make interior transitions into fixed bands natural, with no straight, wavy or polygonal tone seams. {features}
Do not alter leaves, red/gold elements, joints, shadows, stair count, perspective, size, cropping or layout. Do not add objects, symbols, text, buildings, landscape, stairs, vertical grout or UI. No zoom out. Only subtle stone continuity correction; preserve all other pixels. Output native 1254 x 1254.'''
 pp=D/'prompts'/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
 req={'id':name,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'prepared_not_submitted','prompt':prompt,'promptFile':str(pp),'promptSha256':sha(pp),'referenced_image_paths':[e['file'] for e in refs],'references':refs,'targetOriginal':evidence(target,'unmodified original generation'),'northSource':evidence(north,'unified native r10 south overlap; cropped only'),'expectedNativePixels':[1254,1254],'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'builtInOnly':True}
 req['embeddedNeighborSources']=neighbors
 save(D/'prompts'/f'{name}.request.json',req);print(json.dumps({'request':str(D/'prompts'/f'{name}.request.json'),'target':str(seed_path),'references':len(refs)}))
def ingest(col,source):
 name=f'p01_{col:02d}';req=read(D/'prompts'/f'{name}.request.json')
 for ref in req['references']:assert sha(ref['file'])==ref['sha256']
 source=Path(source);destination=D/'native'/f'{name}.png';assert not destination.exists()
 im=Image.open(source);assert im.size==(1254,1254),f'Wrong native size {im.size}';assert im.mode in ('RGB','RGBA')
 if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
 new=np.array(im.convert('RGB'));original=np.array(Image.open(req['targetOriginal']['file']).convert('RGB'));seed=np.array(Image.open(req['references'][0]['file']).convert('RGB'))
 shutil.copyfile(source,destination);assert sha(source)==sha(destination)
 rec={'id':name,'file':str(destination),'sha256':sha(destination),'sourceOutput':str(source),'sourceOutputSha256':sha(source),'width':1254,'height':1254,'mode':im.mode,'format':'PNG','opaque':True,'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','nativePixelsPreserved':True,'resizedAfterGeneration':False,'actualModel':None,'actualQuality':None,'actualSettingsUndisclosed':True,'prompt':req['promptFile'],'promptSha256':req['promptSha256'],'request':str(D/'prompts'/f'{name}.request.json'),'references':req['references'],'originalNative':req['targetOriginal'],'receipt':str(D/'receipts'/f'{name}.receipt.json'),'coordinates':read(T/'native'/f'{name}.png.generation.json')['coordinates'],'pngMetadata':dict(im.info),'visualQa':'pending','selected':False,'fixedBandMeasurements':{}}
 for label,a,b in [('top230VsSeed',new[:230],seed[:230]),('bottom230VsOriginal',new[1024:],original[1024:])]:
  diff=np.abs(a.astype(np.int16)-b.astype(np.int16));rec['fixedBandMeasurements'][label]={'pixelExact':bool(np.array_equal(a,b)),'meanAbsoluteChannelDifference':float(diff.mean()),'differentPixels':int(np.count_nonzero(np.any(a!=b,axis=2)))}
 save(D/'native'/f'{name}.png.generation.json',rec);print(json.dumps({'id':name,'file':str(destination),'sha256':sha(destination),'bands':rec['fixedBandMeasurements']},indent=2))
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','ingest']);p.add_argument('column',type=int);p.add_argument('--source');a=p.parse_args()
if a.action=='prepare':prepare(a.column)
else:ingest(a.column,a.source)
