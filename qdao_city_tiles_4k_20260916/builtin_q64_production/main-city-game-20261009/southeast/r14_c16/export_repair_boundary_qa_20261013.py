from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;D=T/'repairs/roof-local-details-20261013-v1';O=D/'root-boundary-qa';O.mkdir(exist_ok=True)
S=D/'composed-D/candidate-4096.png';I=Image.open(S).convert('RGB');items=[]
boxes={f'south-q{k}':[1024*k,3740,1024*(k+1),4096] for k in range(4)}
boxes.update({'D-bottom':[1750,2448,2890,2960],'D-right':[2548,1520,3060,2774],'D-top':[1930,1354,2954,1866],'D-left':[1924,1520,2436,2774]})
for name,box in boxes.items():
 p=O/(name+'.png');I.crop(box).save(p);items.append({'id':name,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'box':box,'resized':False})
(O/'manifest.json').write_text(json.dumps({'source':str(S),'sourceSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'images':items,'formalAccepted':False},indent=2),encoding='utf-8')
print(json.dumps({'directory':str(O),'images':len(items)}))
