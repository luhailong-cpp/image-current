from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent
a=Image.open(D/'r12c08-rail-v2-actual-core-preview/input-actual-cores.png').convert('RGB')
b=Image.open(D/'r12c08-rail-joint-v4.png').convert('RGB')
rect=(320,125,650,550)
out=D/'r12c08-rail-v4-adoption-preview';out.mkdir(exist_ok=True)
p=a.copy();p.paste(b.crop(rect),rect[:2]);p.save(out/'candidate.png')
for name,box in {'left':(rect[0]-96,rect[1]-64,rect[0]+96,rect[3]+64),'right':(rect[2]-96,rect[1]-64,rect[2]+96,rect[3]+64),'top':(rect[0]-64,rect[1]-64,rect[2]+64,rect[1]+96),'bottom':(rect[0]-64,rect[3]-96,rect[2]+64,rect[3]+64)}.items():
 p.crop(box).save(out/(name+'.png'))
manifest={'candidate':'r12c08-rail-joint-v4.png','nativeAdoptionRect':list(rect),'worldAdoptionRect':[32150+rect[0],44941+rect[1],32150+rect[2],44941+rect[3]],'method':'exact coordinate crop and overwrite for QA only, no resampling or blending','selected':False}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

