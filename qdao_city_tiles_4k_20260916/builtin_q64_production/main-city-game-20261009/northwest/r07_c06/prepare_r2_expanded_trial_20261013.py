from pathlib import Path
from PIL import Image
import json,hashlib
r=Path(__file__).resolve().parent;q=r/'qa/resume-r2c4-expanded05-20261013';q.mkdir(exist_ok=False);base=r/'candidate/r07_c06-candidate-native-roi-v05.png';src=r/'native/s02_04_surfacefix05.png';c=Image.open(base).convert('RGB');s=Image.open(src).convert('RGB');c.paste(s.crop((0,0,1139,1254)),(2957,909));c.save(q/'candidate.png')
boxes={'upper-corner':(2829,781,3405,1357),'lower-junction':(2829,1907,3405,2395),'perimeter-north':(2957,781,4096,1037),'perimeter-south':(2957,2035,4096,2291),'perimeter-west':(2829,909,3085,2163),'band':(2944,1024,3392,2048)}
entries=[]
for name,box in boxes.items():p=q/(name+'.png');c.crop(box).save(p);entries.append(dict(name=name,file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),candidateBox=box,actuallyViewed=False))
(q/'derivation.json').write_text(json.dumps(dict(base=dict(file=str(base),sha256=hashlib.sha256(base.read_bytes()).hexdigest()),newSource=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),sourceROI=[0,0,1139,1254],candidateROI=[2957,909,4096,2163],nativeWorldBox=[23437,25485,24691,26739],trialOnly=True,noResample=True,entries=entries),indent=2),encoding='utf-8')
