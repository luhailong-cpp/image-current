"""Export exact current north boundary pixels, for visual review only."""
from pathlib import Path
from PIL import Image
import json,hashlib
HERE=Path(__file__).resolve().parent;TILE=HERE.parent;ZONE=TILE.parent
OUT=HERE/'north-review';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for c in range(1,5):
    south=TILE/'native'/f'p1{c}.png';north=ZONE/'r07_c13/native'/f'p4{c}.png'
    if not south.exists() or not north.exists():continue
    n=Image.open(north).convert('RGB');s=Image.open(south).convert('RGB');assert n.size==s.size==(1254,1254)
    image=Image.new('RGB',(1024,384));image.paste(n.crop((115,947,1139,1139)),(0,0));image.paste(s.crop((115,115,1139,307)),(0,192))
    path=OUT/f'north-c{c}-1to1.png';image.save(path)
    records.append({'file':str(path),'sha256':sha(path),'northSource':str(north),'northSha256':sha(north),'northCrop':[115,947,1139,1139],'southSource':str(south),'southSha256':sha(south),'southCrop':[115,115,1139,307],'resized':False,'pixels':[1024,384],'visualStatus':'unreviewed','note':'native source cores only; re-export with final north candidate before external review'})
(OUT/'evidence.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(records),'directory':str(OUT)}))
