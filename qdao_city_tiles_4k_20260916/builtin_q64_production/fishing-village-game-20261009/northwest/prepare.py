from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for d in ['guides','native','prompts','receipts','qa','tiles']: (ROOT/d).mkdir(parents=True,exist_ok=True)
ref=Path(CONTRACT['layoutReference'])
im=Image.open(ref); assert im.size==(1254,1254)
assert sha(ref)==CONTRACT['layoutSha256']
assert sha(CONTRACT['detailStyleReference'])==CONTRACT['detailSha256']
tiles=[]
for r in range(1,8):
 for c in range(1,8):
  x,y=(c-1)*4096,(r-1)*4096
  tiles.append({'id':f'r{r:02d}_c{c:02d}','origin':[x,y],'coreBox':[x,y,x+4096,y+4096],'state':'pending'})
write(ROOT/'tile-plan.json',{'zone':'northwest','target4kCount':49,'tiles':tiles,'firstTile':'r03_c03','nativePlan':CONTRACT['nativePatchPlan'],'coordinateConvention':'half-open'})
for ident,box in [('r03_c03', [8192,8192,12288,12288]),('r03_c03_s01_s01',[8077,8077,9331,9331])]:
 ob=[v*1254/57344 for v in box]
 p=ROOT/'guides'/f'{ident}.layout-only.png'
 im.transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC).save(p)
 write(Path(str(p)+'.derivation.json'),{'file':str(p),'sha256':sha(p),'role':'layout-only: resampled coarse map pixels; never final artwork','derivedFrom':[{'file':str(ref),'sha256':sha(ref)}],'operation':'fractional extent crop resampled only for positional guide','globalBox':box,'overviewFractionalBox':ob,'outputPixels':[1254,1254]})
write(ROOT/'progress.json',{'zone':'northwest','status':'preparing-first-native','updatedAt':datetime.now(timezone.utc).isoformat(),'target4kCount':49,'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'currentTile':'r03_c03','currentPatch':'s01_s01','nextStep':'Built-in image_gen first exact-coordinate native patch; measure result then continue using adjacent overlap','errors':[],'worldSizeValidated':False,'navigationValidated':False,'capacity5000Validated':False})
print(json.dumps({'zone':str(ROOT),'guide':str(ROOT/'guides/r03_c03_s01_s01.layout-only.png'),'referenceDimensions':list(im.size)},ensure_ascii=False))

