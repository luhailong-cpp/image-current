"""Native diagnostic crops only; no generation or final-art replacement."""
from pathlib import Path
from PIL import Image
import json, hashlib
Z=Path(__file__).resolve().parents[1]
out=Z/'qa/cross_r05r06_railing_inspection_20261013_v1'
out.mkdir(exist_ok=False)
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
left=Z/'tiles/r06_c03_candidate-v7_4096.png'
right=Z/'tiles/r06_c04_candidate-v8_4096.png'
sources=[info(left),info(right)]
im=Image.new('RGB',(8192,4096));im.paste(Image.open(left),(0,0));im.paste(Image.open(right),(4096,0))
items=[]
for name,box in [('pillar_left',(3120,500,4374,1754)),('rail_west',(3970,350,5224,1604)),('rail_mid',(4646,0,5900,1254)),('rail_east',(5696,0,6950,1254))]:
 p=out/(name+'.png');im.crop(box).save(p)
 items.append(dict(name=name,cropBox=list(box),image=info(p),nativeSize=[1254,1254],resizing=False))
(out/'index.json').write_text(json.dumps(dict(operation='diagnostic same-coordinate exact native crop',isFinalArt=False,sources=sources,items=items),indent=2)+'\n')
print(json.dumps(items))
