from PIL import Image
from pathlib import Path
import json,hashlib
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');out=r/'qa/s02_02_orphanfix01-proposal01';out.mkdir(exist_ok=False)
orig=r/'native/s02_02_resume02.png';don=r/'native/s02_02_orphanfix01.png'
a=Image.open(orig).convert('RGB');d=Image.open(don).convert('RGB');p=a.copy()
rois=[(180,340,265,410),(160,645,255,750)]
for i,box in enumerate(rois,1):
 p.paste(d.crop(box),box[:2])
p.save(out/'proposal-native-1254.png')
for i,box in enumerate(rois,1):
 x0,y0,x1,y1=box;p.crop((x0-25,y0-25,x1+25,y1+25)).save(out/('joint-'+str(i)+'-all-four-perimeters.png'))
rec=dict(status='proposal-only-two-of-four-defects',sourceOriginal=str(orig),additionalNative=str(don),sourceROIs=[list(z) for z in rois],nativeWorldBox=[21389,25485,22643,26739],otherTwoRequestedDefectsPersist=True,formalAccepted=False)
(out/'proposal-proof.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
