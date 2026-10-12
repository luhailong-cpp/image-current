import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent.parent
Q=Z/'qa/r07_c14'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':str(p).replace('\\','/'),'sha256':sha(p)}
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(Q/'manifest.json');active=read(Z/'records/active-candidates.json')['tiles']
imgs={};proof={}
for t in ['r07_c14','r07_c13','r06_c14','r06_c13']:
 p=Path(active[t]['path']);assert sha(p)==active[t]['sha256'];imgs[t]=Image.open(p).convert('RGB');proof[t]=ref(p)
a=imgs['r07_c14'];assert a.size==(4096,4096)
checks=[]
for x in m['inputs']:
 p=Path(x['path']);assert sha(p)==x['sha256'];n=Image.open(p).convert('RGB');assert n.size==(1254,1254)
 assert n.crop(x['nativeCropBox']).tobytes()==a.crop(x['destinationBox']).tobytes()
 checks.append({'kind':'native_patch','id':x['patchId'],**ref(p),'pixelIdentityToCandidate':True})
for x in m['qa']:
 p=Path(x['file']);assert sha(p)==x['sha256'];assert Image.open(p).convert('RGB').tobytes()==a.crop(x['candidateCropBox']).tobytes()
 checks.append({'kind':x['kind'],**ref(p),'pixelIdentityToCandidate':True})
ex=read(Q/'external-boundaries.manifest.json');external=[]
for e in ex['edges']:
 i=e['segment']-1;p=Path(e['output']['path']);assert sha(p)==e['output']['sha256']
 if e['side']=='top':
  b=Image.new('RGB',(1024,256));b.paste(imgs['r06_c14'].crop((i*1024,3968,(i+1)*1024,4096)),(0,0));b.paste(a.crop((i*1024,0,(i+1)*1024,128)),(0,128))
 else:
  b=Image.new('RGB',(256,1024));b.paste(imgs['r07_c13'].crop((3968,i*1024,4096,(i+1)*1024)),(0,0));b.paste(a.crop((0,i*1024,128,(i+1)*1024)),(128,0))
 assert Image.open(p).convert('RGB').tobytes()==b.tobytes(),p
 external.append({'kind':'external_segment','side':e['side'],'segment':i+1,**ref(p),'pixelIdentityToActiveNeighbors':True})
for side in ['north','west']:
 for i in range(1,4):
  v=i*1024;b=Image.new('RGB',(512,512))
  if side=='north':
   b.paste(imgs['r06_c14'].crop((v-256,3840,v+256,4096)),(0,0));b.paste(a.crop((v-256,0,v+256,256)),(0,256))
  else:
   b.paste(imgs['r07_c13'].crop((3840,v-256,4096,v+256)),(0,0));b.paste(a.crop((0,v-256,256,v+256)),(256,0))
  p=Q/f'east-resume-external-{side}-junction{i}.native-1to1.png';assert not p.exists();b.save(p);external.append({'kind':'external_junction','side':side,**ref(p),'pixelScale':1})
b=Image.new('RGB',(512,512));b.paste(imgs['r06_c13'].crop((3840,3840,4096,4096)),(0,0));b.paste(imgs['r06_c14'].crop((0,3840,256,4096)),(256,0));b.paste(imgs['r07_c13'].crop((3840,0,4096,256)),(0,256));b.paste(a.crop((0,0,256,256)),(256,256));p=Q/'east-resume-external-northwest-junction.native-1to1.png';assert not p.exists();b.save(p);external.append({'kind':'external_four_tile_junction',**ref(p),'pixelScale':1})
write(Q/'east-resume-mechanical-audit-20261013.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/east_resume','candidates':proof,'internal':checks,'external':external,'formalAccepted':False,'visualReview':'pending; mechanical validation only'})
print(json.dumps({'internal':len(checks),'external':len(external),'candidate':proof['r07_c14'],'exactPixels':True}))
