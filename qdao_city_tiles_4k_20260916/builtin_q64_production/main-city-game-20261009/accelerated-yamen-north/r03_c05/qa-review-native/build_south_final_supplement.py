from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'south-final-supplement-ac954e1d5fbb'
OUT.mkdir(exist_ok=True)
sources={
 'north':ROOT/'r03_c05/candidate/r03_c05-pipeline-minimum-error-ece82fe09771-fbbe92.png',
 'south':ROOT/'r04_c05/candidate/r04_c05-pipeline-minimum-error-e2769dba9467-6e5fcf.png',
}
expected={'north':'60ecd41051d16e950bd301453236cec3cd0227945ac8d034b9e379e6fce89760','south':'ac954e1d5fbbbcfdba1a0cf4caef511d80a47d6edc5a51271785d8abc78919ac'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
images={}
metadata={}
for k,p in sources.items():
 assert sha(p)==expected[k]
 images[k]=Image.open(p).convert('RGB'); assert images[k].size==(4096,4096)
 metadata[k]={'file':str(p),'sha256':sha(p),'pixels':[4096,4096]}
batch=Image.new('RGB',(1024,1392),'#e8e8e8'); draw=ImageDraw.Draw(batch)
items=[]
for i in range(4):
 q=i*1024; strip=Image.new('RGB',(1024,320))
 nb=[q,3936,q+1024,4096]; sb=[q,0,q+1024,160]
 strip.paste(images['north'].crop(nb),(0,0)); strip.paste(images['south'].crop(sb),(0,160))
 name=f'south-segment{i+1:02d}'; p=OUT/(name+'.png'); strip.save(p)
 draw.text((8,i*348+7),name+' | latest candidates | 1:1 | boundary y=160',fill='black')
 batch.paste(strip,(0,i*348+28))
 items.append({'id':name,'file':str(p),'sha256':sha(p),'sourceBoxes':{'north':nb,'south':sb},'worldBox':[16384+q,12128,17408+q,12448],'pixels':[1024,320],'scale':1,'interpolation':'none','formalBoundaryDisplayY':160})
batch.save(OUT/'south-latest-batch-native.png')
(OUT/'crop-manifest.json').write_text(json.dumps({'sources':metadata,'items':items,'operation':'Exact original-pixel crop/paste; no resizing or modification of source pixels. Labels added only outside imagery.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)
