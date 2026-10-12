import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest");q=z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
a=read(q/'joint-r09c04-c05-finalrail-v1-trace.json')
b=read(q/'joint-r09c05-r10c05-v1-trace.json')
ap=Path(a['context']['path']);bp=Path(b['tiles'][0]['context']['path'])
assert sha(ap)==a['context']['sha256'] and sha(bp)==b['tiles'][0]['context']['sha256']
old=np.array(Image.open(ap).convert('RGB'));new=np.array(Image.open(bp).convert('RGB'))
assert old.shape==(4326,8422,3) and new.shape==(4326,4326,3)
assert np.array_equal(old[:4096,4096:],new[:4096]),'Only shared southern overlap may differ'
after=old.copy();after[:,4096:]=new
p=q/'joint-r09c04-c05-northjoined-v1-context-native.png';assert not p.exists();Image.fromarray(after).save(p)
change=np.any(after!=old,axis=2)
ys,xs=np.where(change)
v={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'exact native replacement of right4326 context from accepted c05 north/south joint; unchanged rows0..4095','baseJoint':a['context'],'updatedRightContext':b['tiles'][0]['context'],'provenance':[ref(q/'joint-r09c04-c05-finalrail-v1-trace.json'),ref(q/'joint-r09c05-r10c05-v1-trace.json')],'context':{**ref(p),'size':[8422,4326],'globalBox':[12173,32653,20595,36979]},'destinationBox':[4096,0,8422,4326],'changedPixelCount':int(change.sum()),'changedContextBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'sourcePixelIdentity':True,'noResize':True,'noDrawing':True,'northSouthQaRootReview':'post native crop and five original-scale shared sections all viewed; continuous wooden post and road/sand transition','formalAcceptedCount':0}
(q/'joint-r09c04-c05-northjoined-v1-trace.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'context':v['context'],'changed':v['changedContextBox']}))

