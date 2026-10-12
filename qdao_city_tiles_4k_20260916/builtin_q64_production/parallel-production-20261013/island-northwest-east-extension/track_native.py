from pathlib import Path
from PIL import Image
import json,hashlib,datetime,sys,shutil
R=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
coords=json.loads((R/'coordinates.json').read_text())
cmd=sys.argv[1]
if cmd=='save':
 stem,src=sys.argv[2:4]; dst=R/'native'/f'{stem}_a01.png'
 if dst.exists(): raise RuntimeError('Refuse overwrite')
 shutil.copy2(src,dst); size=list(Image.open(dst).size)
 record={'id':stem,'file':str(dst),'sourcePath':src,'sha256':sha(dst),'actualNativeDimensions':size,'plannedNativeDimensions':[1254,1254],'coreBoxInNative':[115,115,1139,1139],'sizeContractPass':size==[1254,1254],'route':'built-in image_gen','actualModel':'not_returned','actualQuality':'not_returned','submittedModelSelector':None,'promptFile':str(R/'prompts'/f'{stem}_a01.txt'),'referenceRecord':str(R/'prompts'/f'{stem}_a01.references.json'),'savedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'visualStatus':'candidate_pending_internal_and_external_seam_review','formalAccepted':False,'resized':False}
 write(R/'receipts'/f'{stem}_a01.json',record)
 saved=list((R/'receipts').glob('*_a01.json'))
 write(R/'progress.json',{'status':'native_production','tiles':['r03_c05','r04_c05'],'targetCoreCount':32,'savedNativeCount':len(saved),'formalAcceptedCount':0,'currentPatch':stem,'actualModel':'not_returned','updatedAtUtc':record['savedAtUtc']})
 print(json.dumps(record))
elif cmd=='context':
 stem=sys.argv[2]; c=next(x for x in coords if x['id']==stem);im=Image.open(c.get('westBoundaryContext',c['guide'])).convert('RGB');r=c['subrow'];col=c['subcolumn'];tile=c['tile'];neighbors=[]
 if col>1:
  p=R/'native'/f'{tile}_s{r:02d}_{col-1:02d}_a01.png'
  if p.exists(): im.paste(Image.open(p).crop((1024,0,1254,1254)),(0,0));neighbors.append({'role':'left 230px native overlap','path':str(p),'sha256':sha(p)})
 if r>1:
  p=R/'native'/f'{tile}_s{r-1:02d}_{col:02d}_a01.png'
  if p.exists(): im.paste(Image.open(p).crop((0,1024,1254,1254)),(0,0));neighbors.append({'role':'top 230px native overlap','path':str(p),'sha256':sha(p)})
 elif tile=='r04_c05':
  p=R/'native'/f'r03_c05_s04_{col:02d}_a01.png'
  if p.exists(): im.paste(Image.open(p).crop((0,1024,1254,1254)),(0,0));neighbors.append({'role':'top 230px native overlap','path':str(p),'sha256':sha(p)})
 dst=R/'guides'/f'{stem}.continuity-context.png';im.save(dst);write(dst.with_suffix('.json'),{'coordinate':c,'neighbors':neighbors,'purpose':'Only native overlap strips are real detail; remaining is layout-only proxy','sha256':sha(dst)});print(str(dst))
