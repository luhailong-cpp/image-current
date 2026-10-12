"""Exact 1:1 final candidate seam windows and lossless review montages."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent;TILE=HERE.parents[1];ZONE=TILE.parent
source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(source).convert('RGB');assert im.size==(4096,4096);records=[]
def crop(name,box,kind):
    p=out/(name+'.png');part=im.crop(box);part.save(p);records.append({'id':name,'file':str(p),'sha256':sha(p),'tileBox':box,'kind':kind,'pixelsPerSourcePixel':1});return part
for boundary in range(1,4):
    v=Image.new('RGB',(920,1024));h=Image.new('RGB',(1024,920))
    for i in range(4):
        x=boundary*1024
        a=crop(f'v{boundary}-r{i+1}',[x-115,i*1024,x+115,(i+1)*1024],'internal pair');v.paste(a,(230*i,0))
        a=crop(f'h{boundary}-c{i+1}',[i*1024,x-115,(i+1)*1024,x+115],'internal pair');h.paste(a,(0,230*i))
    v.save(out/f'v{boundary}-montage-1to1.png');h.save(out/f'h{boundary}-montage-1to1.png')
j=Image.new('RGB',(690,690))
for r in range(1,4):
    for c in range(1,4):
        a=crop(f'junction-r{r}-c{c}',[c*1024-115,r*1024-115,c*1024+115,r*1024+115],'four-way intersection');j.paste(a,((c-1)*230,(r-1)*230))
j.save(out/'junctions-montage-1to1.png')
northpath=ZONE/'r05_c13/candidates/r05_c13.candidate.png';north=Image.open(northpath).convert('RGB');external=[]
for i in range(4):
    a=Image.new('RGB',(1024,460));a.paste(north.crop([i*1024,3866,(i+1)*1024,4096]),(0,0));a.paste(im.crop([i*1024,0,(i+1)*1024,230]),(0,230));p=out/f'north-shared-c{i+1}-1to1.png';a.save(p);external.append({'file':str(p),'sha256':sha(p),'northCrop':[i*1024,3866,(i+1)*1024,4096],'southCrop':[i*1024,0,(i+1)*1024,230],'joinY':230})
manifest={'candidate':str(source),'sha256':sha(source),'northCandidate':str(northpath),'northSha256':sha(northpath),'internalPairCount':24,'intersectionCount':9,'records':records,'externalNorthShared':external,'formalAcceptedCount':0,'visualStatus':'awaiting-review'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'output':str(out),'candidateSha256':sha(source),'northSha256':sha(northpath),'internalPairCount':24,'intersectionCount':9}))
