from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p): return {'path':str(p),'sha256':sha(p)}
ptr=read(T/'candidate/latest-assembly.json'); m=read(ptr['manifest']['path'])
q=T/'review/native49-56e834ccdf9f6e52a143'; q.mkdir(exist_ok=True)
sources=[]
for s in m['nativeSources']:
 assert sha(s['native'])==s['nativeSha256']
 sources.append(np.asarray(Image.open(s['native']).convert('RGB')))
assert sha(m['seamPathsAndAlpha']['path'])==m['seamPathsAndAlpha']['sha256']
with np.load(m['seamPathsAndAlpha']['path'],allow_pickle=False) as masks:
 def join(a,b,label):
  w=masks[label+'_alpha'].astype(np.uint32)[...,None]
  overlap=((a[:,-230:].astype(np.uint32)*(255-w)+b[:,:230].astype(np.uint32)*w+127)//255).astype(np.uint8)
  return np.concatenate([a[:,:-230],overlap,b[:,230:]],axis=1)
 rows=[]
 for r in range(4):
  a=sources[r*4]
  for c in range(1,4): a=join(a,sources[r*4+c],f'row{r+1:02d}_c{c:02d}_c{c+1:02d}')
  rows.append(a)
 context=rows[0].transpose(1,0,2)
 for r in range(1,4): context=join(context,rows[r].transpose(1,0,2),f'rows_r{r:02d}_r{r+1:02d}')
 context=context.transpose(1,0,2)
assert np.array_equal(context,np.asarray(Image.open(m['context']['path'])))
core=context[115:4211,115:4211]
assert np.array_equal(core,np.asarray(Image.open(m['candidate']['path'])))
im=Image.fromarray(core); regions=[]
def crop(label,box,kind):
 p=q/(label+'.png'); image=im.crop(box)
 if p.exists(): assert np.array_equal(np.asarray(Image.open(p)),np.asarray(image))
 else: image.save(p)
 e=ev(p); e.update(label=label,box=box,kind=kind,resized=False); regions.append(e)
for d in ('vertical','horizontal'):
 for pos in (1024,2048,3072):
  for i in range(4):
   a,b=i*1024,(i+1)*1024
   crop(f'{d}-{pos}-q{i+1}',[pos-256,a,pos+256,b] if d=='vertical' else [a,pos-256,b,pos+256],'internal_seam')
for y in (1024,2048,3072):
 for x in (1024,2048,3072): crop(f'junction-{x}-{y}',[x-450,y-450,x+450,y+450],'junction')
for d in ('north','south','west','east'):
 for i in range(4):
  a,b=i*1024,(i+1)*1024
  crop(f'edge-{d}-q{i+1}',{'north':[a,0,b,256],'south':[a,3840,b,4096],'west':[0,a,256,b],'east':[3840,a,4096,b]}[d],'edge')
assert len(regions)==49
neighbors={}
for d,tile in [('north','r15_c14'),('west','r16_c13')]:
 p=read(T.parent/tile/'candidate/latest-assembly.json')['candidate']
 assert sha(p['path'])==p['sha256']
 other=np.asarray(Image.open(p['path']).convert('RGB'))
 joined=np.concatenate([other[-256:],core[:256]],axis=0) if d=='north' else np.concatenate([other[:,-256:],core[:,:256]],axis=1)
 entries=[]
 for i in range(4):
  part=joined[:,i*1024:(i+1)*1024] if d=='north' else joined[i*1024:(i+1)*1024]
  path=q/f'join-{d}-q{i+1}.png'; Image.fromarray(part).save(path)
  entries.append(ev(path))
 for j in (1024,2048,3072):
  part=joined[:,j-450:j+450] if d=='north' else joined[j-450:j+450]
  path=q/f'join-{d}-intersection-{j}.png'; Image.fromarray(part).save(path); entries.append(ev(path))
 neighbors[d]={'neighbor':p,'reviewImages':entries}
data={'tile':'r16_c14','createdAt':datetime.now(timezone.utc).isoformat(),'manifest':ptr['manifest'],'candidate':m['candidate'],'context':m['context'],'regions':regions,'neighbors':neighbors,'replay':{'sourcesVerified':16,'contextPixelIdentical':True,'corePixelIdentical':True,'savedAlphaVerified':True,'resize':False,'rgbCorrection':False},'visualQA':'pending','formalAccepted':False}
(q/'index.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qaDirectory':str(q),'regions':len(regions),'neighborImages':14,'replay':data['replay']},indent=2))
