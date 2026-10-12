from pathlib import Path
import json,hashlib,os
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
L=read(T/'candidate/latest-assembly.json')
assert 'b7991325a75381cebe45' in L['candidate']['path']
assert sha(Path(L['candidate']['path']))==L['candidate']['sha256']
C=Image.open(L['candidate']['path']).convert('RGB')
O=T/'review/root-native-full-qa-20261012';O.mkdir(exist_ok=True)
items=[]
def save(name,im,basis):
 p=O/(name+'.png')
 if not p.exists():
  with p.open('xb') as f:im.save(f,format='PNG')
 assert Image.open(p).convert('RGB').tobytes()==im.tobytes()
 items.append({'id':name,'path':str(p),'sha256':sha(p),'size':list(im.size),'basis':basis,'resized':False})
for v in (1024,2048,3072):
 for k in range(4):
  box=[k*1024,v-256,(k+1)*1024,v+256]
  save(f'h{v}-q{k}',C.crop(box),{'candidateCrop':box})
  box=[v-256,k*1024,v+256,(k+1)*1024]
  save(f'v{v}-q{k}',C.crop(box),{'candidateCrop':box})
for sy in (1024,2048,3072):
 for sx in (1024,2048,3072):
  box=[sx-450,sy-450,sx+450,sy+450]
  save(f'j{sx}-{sy}',C.crop(box),{'candidateCrop':box})
for edge in ('north','south','west','east'):
 for k in range(4):
  box={'north':[k*1024,0,(k+1)*1024,256],'south':[k*1024,3840,(k+1)*1024,4096],'west':[0,k*1024,256,(k+1)*1024],'east':[3840,k*1024,4096,(k+1)*1024]}[edge]
  save(f'edge-{edge}-q{k}',C.crop(box),{'candidateCrop':box})
Wpath=Path(read(T.parent/'r13_c15/progress.json')['candidate'])
assert sha(Wpath)=='173e67ac86c37595dd6ad272757093367dab48585f73c8192c832fcf3f42110f'
W=Image.open(Wpath).convert('RGB')
for k in range(4):
 im=Image.new('RGB',(640,1024));im.paste(W.crop((3776,k*1024,4096,(k+1)*1024)),(0,0));im.paste(C.crop((0,k*1024,320,(k+1)*1024)),(320,0))
 save(f'west-neighbor-q{k}',im,{'west':str(Wpath),'westSha256':sha(Wpath),'boundaryX':320,'yRange':[k*1024,(k+1)*1024]})
d={'candidate':L['candidate'],'assembly':L['manifest'],'images':items,'formalAccepted':False}
p=O/'manifest.json'
if not p.exists():
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
else:assert read(p)==d
print(json.dumps({'directory':str(O),'images':len(items),'manifestSha256':sha(p)}))
