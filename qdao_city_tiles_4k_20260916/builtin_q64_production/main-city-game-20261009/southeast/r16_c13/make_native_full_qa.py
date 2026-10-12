from pathlib import Path
import json, hashlib, numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
L=json.loads((T/'candidate/latest-assembly.json').read_text())
C=Image.open(L['candidate']['path']).convert('RGB')
M=json.loads(Path(L['manifest']['path']).read_text(encoding='utf-8-sig'))
O=T/'review'/'native-full-qa-v1'; O.mkdir(exist_ok=True)
items=[]
def save(name,im,basis):
 p=O/(name+'.png'); im.save(p); items.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'basis':basis,'resized':False})
for v in (1024,2048,3072):
 for k in (0,1):
  box=[k*2048,v-256,(k+1)*2048,v+256]
  save(f'horizontal-y{v}-half{k+1}',C.crop(box),{'candidateCrop':box})
  box=[v-256,k*2048,v+256,(k+1)*2048]
  save(f'vertical-x{v}-half{k+1}',C.crop(box),{'candidateCrop':box})
for edge in ('north','south','west','east'):
 for k in (0,1):
  box={'north':[k*2048,0,(k+1)*2048,256],'south':[k*2048,3840,(k+1)*2048,4096],'west':[0,k*2048,256,(k+1)*2048],'east':[3840,k*2048,4096,(k+1)*2048]}[edge]
  save(f'edge-{edge}-half{k+1}',C.crop(box),{'candidateCrop':box})
Npath=T.parent/'r15_c13/candidate/r15_c13-4k-native-halo24-v4-20261012.png'
N=Image.open(Npath).convert('RGB')
for k in range(4):
 im=Image.new('RGB',(1024,640)); im.paste(N.crop((k*1024,3776,(k+1)*1024,4096)),(0,0)); im.paste(C.crop((k*1024,0,(k+1)*1024,320)),(0,320))
 save(f'north-neighbor-quarter{k+1}',im,{'north':str(Npath),'northSha256':hashlib.sha256(Npath.read_bytes()).hexdigest(),'boundaryY':320,'xRange':[k*1024,(k+1)*1024]})
(O/'manifest.json').write_text(json.dumps({'candidate':L['candidate'],'assembly':L['manifest'],'images':items,'formalAccepted':False},indent=2))
print(json.dumps({'directory':str(O),'images':len(items),'masksKeys':M['seamPathsAndAlpha']['arrayKeys']}))

