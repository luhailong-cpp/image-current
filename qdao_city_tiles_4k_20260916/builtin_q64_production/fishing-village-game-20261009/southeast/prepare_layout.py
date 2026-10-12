"""Mechanical coordinate guides only. No guide pixels may enter final artwork."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ZONE = Path(__file__).resolve().parent
ROOT = ZONE.parents[3]
CONTRACT = json.loads((ZONE.parent / 'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save_json(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
refs = [
    {'path': CONTRACT['layoutReference'], 'role':'authoritative full-map layout only'},
    {'path': CONTRACT['detailStyleReference'], 'role':'material and daylight detail style; independent close-up, NOT coordinate crop'},
    {'path': CONTRACT['primaryStyleReference'], 'role':'primary approved rounded painterly style only; do not copy UI or night lighting'},
]
for ref in refs: ref['sha256'] = sha(ref['path'])
assert refs[0]['sha256'] == CONTRACT['layoutSha256']
assert refs[1]['sha256'] == CONTRACT['detailSha256']
im = Image.open(refs[0]['path'])
assert im.size == (1254,1254)
scale = 1254 / 57344
tile = 'r10_c09'
guide_dir = ZONE / tile / 'layout-only'
guide_dir.mkdir(parents=True, exist_ok=True)
patches = []
for sr in range(1,5):
    for sc in range(1,5):
        x,y = 32768+(sc-1)*1024,36864+(sr-1)*1024
        box = [x-115,y-115,x+1139,y+1139]
        refbox = [v*scale for v in box]
        out = guide_dir / f'p{sr}{sc}-layout-only.png'
        im.transform((1254,1254), Image.Transform.EXTENT, refbox, Image.Resampling.BICUBIC).save(out)
        record = {'file':str(out), 'sha256':sha(out), 'classification':'layout-only, never final artwork', 'operation':'uniform mechanical extent crop/resample from overview', 'derivedFrom':refs[0], 'outputDimensions':[1254,1254], 'globalBox':box, 'overviewBox':refbox, 'coreBox':[x,y,x+1024,y+1024]}
        save_json(out.with_suffix('.png.derivation.json'),record)
        patches.append({'id':f'p{sr}{sc}','subrow':sr,'subcolumn':sc,**record})
tilebox = [32768,36864,36864,40960]
tileguide = guide_dir / 'r10_c09-layout-only.png'
im.transform((1024,1024),Image.Transform.EXTENT,[v*scale for v in tilebox],Image.Resampling.BICUBIC).save(tileguide)
save_json(tileguide.with_suffix('.png.derivation.json'), {'classification':'layout-only, never final artwork','operation':'uniform overview crop/resample','derivedFrom':refs[0], 'globalBox':tilebox,'outputDimensions':[1024,1024], 'sha256':sha(tileguide)})
save_json(ZONE/'coordinate-plan.json', {'createdAt':now(),'tile':tile,'tileCoreBox':tilebox,'referenceSize':[1254,1254], 'artCanvasPixels':[57344,57344],'expectedNativeSize':[1254,1254],'corePixels':1024,'haloPixels':115,'adjacentOverlapPixels':230,'resizeFinalArtAllowed':False,'references':refs,'patches':patches})
save_json(ZONE/'progress.json', {'updatedAt':now(),'zone':'southeast','status':'preparing_first_native','target4kCount':49,'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'currentTile':tile,'currentPatch':'p11','nextStep':'Generate p11 using exact layout guide and all three approved references; measure output; then extend sequentially with native overlap','actualErrors':[],'capacity5000Validated':False,'clientMappingValidated':False})
print(json.dumps({'zone':str(ZONE),'guides':len(patches),'firstPatch':patches[0],'references':refs},ensure_ascii=False,indent=2))
