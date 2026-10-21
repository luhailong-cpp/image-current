import sys
sys.dont_write_bytecode=True
import json,hashlib,importlib.util
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent;repo=z.parents[3]
sp=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(sp);sp.loader.exec_module(prod)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
patch=sys.argv[1];stem='r12_c05_'+patch+'_v1'
assert not (z/'native'/(stem+'.png')).exists()
assert not (z/'native'/(stem+'.request.json')).exists(),'Prepared request already exists'
rules=[]
for rel,expected in [('AGENTS.md','57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a'),('docs/MAP_PARALLEL_SPLIT_20261013.json','a7cab49b89974586a1a0375baeadc5d4a7aa12dce6e782bcc8f9b52b777b3c8f')]:
 p=repo/rel;content=p.read_bytes();actual=hashlib.sha256(content).hexdigest()
 if actual!=expected:print(content.decode('utf-8-sig'));raise SystemExit('Rules changed: review before continuing')
 rules.append({'path':p.as_posix(),'sha256':actual,'readBeforeRequest':True})
split=read(repo/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert not any('r12_c05' in b['tiles'] for b in split['batches'] if b.get('status')=='allocated_root_reserved')
prod.prepare('r12_c05',patch,'v1')
rp=z/'native'/(stem+'.request.json');r=read(rp);b=r['coordinates']['globalContextBox'];dst=Path(r['references'][0]['path']);canvas=Image.open(dst).convert('RGB');anchors=[]
tile='r11_c05';source=z/'qa/block2x2-r10r11c05c06-v1-r11_c05-context-native.png'
box=[16269,40845,20595,45171];i=[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]
if i[2]>i[0] and i[3]>i[1]:
 with Image.open(source) as im:
  assert im.size==(4326,4326)
  canvas.paste(im.crop((i[0]-box[0],i[1]-box[1],i[2]-box[0],i[3]-box[1])),(i[0]-b[0],i[1]-b[1]))
 anchors.append({'path':source.as_posix(),'sha256':prod.sha(source),'tile':tile,'globalOverlapBox':i,'operation':'integer crop and paste only'})
canvas.save(dst);r['currentFinalAnchors']=anchors;r['rulesReadBeforeRequest']=rules;prod.write(rp,r)
dp=Path(str(dst)+'.derivation.json');d=read(dp);d.update({'sha256':prod.sha(dst),'currentFinalAnchors':anchors});prod.write(dp,d)
print(json.dumps({'stem':stem,'guide':dst.as_posix(),'anchors':anchors,'rules':rules}))
