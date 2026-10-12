import sys
sys.dont_write_bytecode=True
import json,hashlib,importlib.util,re
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent;repo=z.parents[3]
sp=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(sp);sp.loader.exec_module(prod)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':prod.sha(p)}
patch=sys.argv[1];stem='r11_c04_'+patch+'_v1'
assert not (z/'native'/(stem+'.png')).exists()
assert not (z/'native'/(stem+'.request.json')).exists(),'Do not overwrite prepared request'
split=read(repo/'docs/MAP_PARALLEL_SPLIT_20261013.json')
assert not any('r11_c04' in b['tiles'] for b in split['batches'] if b.get('status')=='allocated_root_reserved')
prod.prepare('r11_c04',patch,'v1')
rp=z/'native'/(stem+'.request.json');r=read(rp);b=r['coordinates']['globalContextBox'];dst=Path(r['references'][0]['path']);canvas=Image.open(dst).convert('RGB');anchors=[]
for tile,source in [('r10_c04','block2x2-r09r10c03c04-v1-r10_c04-context-native.png'),('r11_c03','pair-r10c03-r11c03-v1-r11_c03-context-native.png'),('r11_c05','block2x2-r10r11c05c06-v1-r11_c05-context-native.png')]:
 rr,cc=int(tile[1:3]),int(tile[5:7]);box=[(cc-1)*4096-115,(rr-1)*4096-115,cc*4096+115,rr*4096+115];i=[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]
 if i[2]<=i[0] or i[3]<=i[1]:continue
 src=z/'qa'/source
 with Image.open(src) as im:canvas.paste(im.crop((i[0]-box[0],i[1]-box[1],i[2]-box[0],i[3]-box[1])),(i[0]-b[0],i[1]-b[1]))
 anchors.append({**ref(src),'tile':tile,'globalOverlapBox':i,'targetBox':[i[0]-b[0],i[1]-b[1],i[2]-b[0],i[3]-b[1]],'operation':'integer crop and paste; no resampling'})
canvas.save(dst);r['currentFinalAnchors']=anchors;r['rulesReadBeforeRequest']=[ref(repo/'AGENTS.md'),ref(repo/'docs/MAP_PARALLEL_SPLIT_20261013.json')];prod.write(rp,r)
dp=Path(str(dst)+'.derivation.json');d=read(dp);d.update({'sha256':prod.sha(dst),'currentFinalAnchors':anchors});prod.write(dp,d)
print(json.dumps({'stem':stem,'guide':dst.as_posix(),'anchors':anchors,'rules':r['rulesReadBeforeRequest']}))
