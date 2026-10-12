from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repairs/shore-water-join-20261012-v1';O=D/'root-changed-evidence';O.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(D/'composition.json');baseqa=read(T/'review/root-native-full-qa-20261012/manifest.json')
C=Image.open(m['candidate']['path']).convert('RGB');items=[];unchanged=[]
for e in baseqa['images']:
 if 'candidateCrop' not in e['basis']:
  unchanged.append(e['id']);continue
 new=C.crop(e['basis']['candidateCrop'])
 old=Image.open(e['path']).convert('RGB')
 if np.array_equal(np.array(new),np.array(old)):
  unchanged.append(e['id']);continue
 p=O/(e['id']+'.png')
 if not p.exists():
  with p.open('xb') as f:new.save(f,format='PNG')
 assert Image.open(p).tobytes()==new.tobytes()
 items.append({'id':e['id'],'path':str(p),'sha256':sha(p),'pixels':list(new.size),'resized':False,'candidateCrop':e['basis']['candidateCrop']})
d={'candidate':m['candidate'],'changedEvidence':items,'pixelIdenticalEvidenceCarriedForward':unchanged,'baseEvidenceCount':len(baseqa['images'])}
p=O/'manifest.json'
if not p.exists():
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps(d))
