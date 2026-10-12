"""Mechanical layout crops and provenance only. No drawing or final-art upscaling."""
from pathlib import Path
from PIL import Image
import json, hashlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
PROJECT = Path('D:/work/image')
CONTRACT = json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p, value):
    Path(p).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['guides','prompts','native','receipts','qa','tiles']:
    (ROOT/name).mkdir(parents=True,exist_ok=True)
refs = []
for field,role in [('layoutReference','sole global layout'),('detailStyleReference','material and architecture only; independent closeup, not coordinate layout'),('primaryStyleReference','primary approved painterly style only; no UI or night lighting')]:
    p=Path(CONTRACT[field]); im=Image.open(p)
    refs.append(dict(path=p.as_posix(),role=role,sha256=sha(p),nativeSize=list(im.size)))
assert refs[0]['sha256']==CONTRACT['layoutSha256']
assert refs[1]['sha256']==CONTRACT['detailSha256']
im=Image.open(CONTRACT['layoutReference']).convert('RGB')
patch='r03_c03_s01_01'
box=[8077,8077,9331,9331]
refbox=[v*1254/57344 for v in box]
guide=ROOT/'guides'/f'{patch}.layout-only.png'
im.transform((1254,1254),Image.Transform.EXTENT,refbox,Image.Resampling.BICUBIC).save(guide)
write_json(guide.with_suffix('.png.derivation.json'),dict(file=guide.as_posix(),sha256=sha(guide),purpose='layout-only; forbidden as final art',derivedFrom=refs[0],operation='floating-coordinate extent crop, bicubic enlargement for layout input only',globalBox=box,referenceBox=refbox,outputSize=[1254,1254]))
write_json(ROOT/'references.json',refs)
write_json(ROOT/'coordinates.json',dict(tile='r03_c03',tileBox=[8192,8192,12288,12288],firstPatch=patch,coreBox=[8192,8192,9216,9216],nativeBox=box,referenceBox=refbox,plannedCore=1024,plannedHalo=115,plannedNative=1254,measurementPending=True))
write_json(ROOT/'progress.json',dict(zone='northwest',status='preparing_first_native',target4kCount=49,generatedNativeCount=0,usableNativeCount=0,complete4kCount=0,formalAcceptedCount=0,currentTile='r03_c03',currentPatch=patch,nextStep='Generate first precisely located native detail patch with builtin image_gen; measure returned dimensions.',lastError=None,updatedAtUtc=datetime.now(timezone.utc).isoformat()))
print(json.dumps({'guide':str(guide),'references':refs,'referenceBox':refbox},ensure_ascii=False))
