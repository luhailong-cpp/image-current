from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
CONTRACT=json.loads((ROOT/'production-contract.json').read_text(encoding='utf-8-sig'))
REF=Path(CONTRACT['layoutReference'])
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data): Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
for folder in ['r13_c13/layout-only','r13_c13/native','r13_c13/records','r13_c13/review']:
    (BASE/folder).mkdir(parents=True,exist_ok=True)
im=Image.open(REF).convert('RGB')
tile=[49152,49152,53248,53248]
def guide(bounds,path):
    box=[v*im.width/65536 for v in bounds]
    im.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.NEAREST).save(path)
    write(str(path)+'.derived.json',{'role':'layout-only; never game pixels','derivedFrom':{'path':str(REF),'sha256':sha(REF)},'operation':'extent crop mapped from 65536 artwork coordinates; nearest resample for geometry guide only','artCanvasBox':bounds,'referenceBox':box,'sourceSize':list(im.size),'guideSize':[1254,1254],'sha256':sha(path)})
guide(tile,BASE/'r13_c13/layout-only/tile-layout-only.png')
patches=[]
for r in range(4):
    for c in range(4):
        x=49152+c*1024;y=49152+r*1024
        bounds=[x-115,y-115,x+1139,y+1139]
        name=f'p{r+1:02d}_{c+1:02d}'
        guide(bounds,BASE/f'r13_c13/layout-only/{name}-layout-only.png')
        patches.append({'id':name,'row':r+1,'column':c+1,'coreBox':[x,y,x+1024,y+1024],'contextBox':bounds,'nativeExpected':[1254,1254],'coreCropExpected':[115,115,1139,1139]})
write(BASE/'r13_c13/coordinates.json',{'tile':'r13_c13','coreBox':tile,'coordinateAuthority':str(ROOT/'production-contract.json'),'referenceSha256':sha(REF),'patches':patches})
write(BASE/'model-verification.json',{'checkedAt':now(),'sources':['https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','https://developers.openai.com/api/docs/guides/tools-image-generation'],'finding':'Official docs list gpt-image-2.5-sunburst and max. Batch follows existing configuration; builtin tool exposes no model or quality selectors.','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'actualModel':None,'actualQuality':None})
write(BASE/'progress.json',{'zone':'southeast','status':'generating_first_native_patch','updatedAt':now(),'tileRows':[9,16],'tileColumns':[9,16],'firstTile':'r13_c13','generatedNativeCount':0,'complete4kCandidateCount':0,'formalAcceptedCount':0,'nextStep':'Generate r13_c13 p01_01 then extend adjacent native overlap, measure each output before assembly.','currentTile':'r13_c13','currentPatch':'p01_01','worldSize':None,'clientMappingValidated':False,'capacity5000Validated':False})
print(json.dumps({'tileBox':tile,'referenceSize':im.size,'firstPatch':patches[0]}))
