from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/checkpoint-20261013-v1';Q.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=[T/'native/p41-v4.png',T/'native/p42-v2.png',T.parent/'r09_c09/processed/colorpass-20261012-v1/p11-colorpass.png',T.parent/'r09_c09/processed/colorpass-20261012-v1/p12-colorpass.png']
canvas=Image.new('RGB',(2048,2048))
for i,p in enumerate(src):canvas.paste(Image.open(p).crop((115,115,1139,1139)),((i%2)*1024,(i//2)*1024))
records=[]
for name,box in [('p41--p42',[768,0,1280,1024]),('south-segment-1',[0,768,1024,1280]),('south-segment-2',[1024,768,2048,1280]),('south-cross-p41-p42-r09p11-p12',[768,768,1280,1280])]:
    p=Q/(name+'-100pct.png');canvas.crop(box).save(p)
    d=dict(file=str(p),sha256=sha(p),globalBox=[32768+box[0],31744+box[1],32768+box[2],31744+box[3]],dimensions=list(Image.open(p).size),resampling=False,operation='Exact native [115,115,1139,1139] core assembly and unscaled crop',sources=[dict(file=str(s),sha256=sha(s)) for s in src],visualReview='pending')
    Path(str(p)+'.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8');records.append(d)
(Q/'manifest.json').write_text(json.dumps(dict(createdAt=datetime.now(timezone.utc).isoformat(),tile='r08_c09',selectedCountBeforeReview=1,recoveredCandidate='p42-v2',evidence=records,formalAccepted=False,internalReady=False),indent=2),encoding='utf-8')
print(json.dumps(dict(directory=str(Q),evidenceCount=len(records))))
