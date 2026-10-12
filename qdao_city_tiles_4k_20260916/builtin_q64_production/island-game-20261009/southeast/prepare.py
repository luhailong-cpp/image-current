"""Mechanical coordinate guides and audit records only; no painted output."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJECT = Path('D:/work/image')
CONTRACT = json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG = json.loads((PROJECT/'config/image-generation.json').read_text(encoding='utf-8-sig'))
def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()

for folder in ['guides','native','prompts','receipts','qa','tiles']:
    (ROOT/folder).mkdir(exist_ok=True)
refs=[]
for field, role, expected in [
    ('layoutReference','sole full-map coordinate and layout reference',CONTRACT['layoutSha256']),
    ('detailStyleReference','independent material and architecture close-up; NOT a coordinate crop',CONTRACT['detailSha256']),
    ('primaryStyleReference','primary approved Q Daoist painting style; no UI, characters or night lighting',None)]:
    p=Path(CONTRACT[field]); actual=sha(p)
    if expected and actual!=expected: raise ValueError(f'Reference hash mismatch: {p}')
    with Image.open(p) as im: size=list(im.size)
    refs.append({'file':p.as_posix(),'role':role,'sha256':actual,'nativePixels':size})
write_json(ROOT/'references.json',refs)
tiles=[]
for r in range(8,15):
    for c in range(8,15):
        tid=f'r{r:02d}_c{c:02d}'
        x=(c-1)*4096;y=(r-1)*4096
        patches=[]
        for sr in range(4):
            for sc in range(4):
                px=x+sc*1024;py=y+sr*1024
                box=[px-115,py-115,px+1139,py+1139]
                patches.append({'id':f'{tid}_p{sr+1}{sc+1}','subrow':sr+1,'subcolumn':sc+1,'coreGlobalBox':[px,py,px+1024,py+1024],'nativeGlobalBox':box,'layoutReferenceBox':[v*1254/57344 for v in box],'expectedNativePixels':[1254,1254],'status':'pending'})
        tiles.append({'id':tid,'row':r,'column':c,'origin':[x,y],'coreGlobalBox':[x,y,x+4096,y+4096],'patches':patches,'status':'pending'})
write_json(ROOT/'coordinate-plan.json',{'schemaVersion':1,'zone':'southeast','artCanvasPixels':[57344,57344],'tiles':tiles,'reference':refs[0],'noResizeFinalArt':True})
tile=next(t for t in tiles if t['id']=='r09_c12')
with Image.open(refs[0]['file']) as im:
    for p in tile['patches']:
        file=ROOT/'guides'/f"{p['id']}.layout-only.png"
        im.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(file)
        write_json(Path(str(file)+'.generation.json'),{'file':file.as_posix(),'sha256':sha(file),'generatedAt':utc(),'width':1254,'height':1254,'format':'PNG','operation':'mechanical fractional-coordinate crop and enlargement, layout-only; never final artwork','derivedFrom':[refs[0]],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
progress={'schemaVersion':1,'zone':'southeast','status':'in_progress','updatedAt':utc(),'assigned4kCount':49,'generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'currentTile':'r09_c12','currentPatch':'r09_c12_p11','nextStep':'Generate first native roof-slope patch using exact layout-only crop and three approved reference inputs','lastError':None,'configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin image_gen exposes no model/quality selectors; actual returned evidence will be recorded per image.','worldAreaRatioToMain':0.75,'worldSize':None,'capacity5000Validated':False,'clientMappingValidated':False}
write_json(ROOT/'progress.json',progress)
print(json.dumps({'references':refs,'firstTile':tile['coreGlobalBox'],'firstPatch':tile['patches'][0]},ensure_ascii=False))
