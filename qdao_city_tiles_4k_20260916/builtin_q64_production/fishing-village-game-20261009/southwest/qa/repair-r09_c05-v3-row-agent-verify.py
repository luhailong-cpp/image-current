import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'path':Path(p).as_posix(),'sha256':sha(p)}
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
trp=z/'qa/repair-r09_c05-v3-trace.json';t=json.loads(trp.read_text())
orig=np.asarray(Image.open(t['baseContext']['path']).convert('RGB'))
out=np.asarray(Image.open(t['context']['path']).convert('RGB'))
ids=np.load(t['completeContextSourceIds']['path'])
assert np.array_equal(orig[ids==0],out[ids==0])
reports=[]
for rr in t['repairsInOrder']:
 tr=json.loads(Path(rr['trace']['path']).read_text())
 b=tr['contextBox'];rid=rr['id']
 qa=z/'qa'/f'repair-r09_c05-v3-{rid}-after-100pct.png'
 Image.fromarray(out[b[1]:b[3],b[0]:b[2]]).save(qa)
 write(str(qa)+'.derivation.json',{'file':qa.as_posix(),'sha256':sha(qa),'source':t['context'],'sourceBox':b,'operation':'integer crop only','noResize':True})
 reports.append({'id':rid,'view':ref(qa),'mask':tr['sourceMask'],'repairBounds':tr['repairBounds'],'tileContextBox':tr['tileContextBox'],'repairPixelCount':tr['repairPixelCount'],'mechanicalValidation':tr['validation']})
# Road boundary sampling: first 5 consecutive warm sand pixels near known diagonal in source sand crop.
b=[565,3072,1819,4326]
a=orig[b[1]:b[3],b[0]:b[2]].astype(int);c=out[b[1]:b[3],b[0]:b[2]].astype(int)
def roadedge(im,x):
 expect=int(0.552*(x-430)+95)
 vals=im[:,:,0]-im[:,:,2]
 for y in range(max(0,expect-25),min(1250,expect+40)):
  if np.all(vals[y:y+5,x]>35):return y
 return None
samples=[{'localX':x,'beforeY':roadedge(a,x),'afterY':roadedge(c,x)} for x in range(475,901,25)]
for s in samples: s['deltaY']=None if s['beforeY'] is None or s['afterY'] is None else s['afterY']-s['beforeY']
# Preserve source metadata records; old sand edit superseded by v2.
gp=z/'native/r09_c05_repair_sand_v1.png.generation.json'
g=json.loads(gp.read_text());g['status']='superseded';g['supersededBy']='r09_c05_repair_sand_v2.png';g['reason']='AI spread orange grain into left anchor, creating visible hard-mask material seam.';write(gp,g)
result={'status':'mechanically_verified_local_visual_review_pending','baseUnchanged':sha(t['baseContext']['path'])==t['baseContext']['sha256'],'output':t['candidate'],'context':t['context'],'trace':ref(trp),'allUnselectedPixelsEqualOriginal':True,'nativeResampling':False,'feather':False,'manualPainting':False,'formalAcceptance':False,'complete4kProgressModified':False,'repairs':reports,'roadEdgeSampling':{'method':'first 5 consecutive pixels R-B>35 within +/- expected original diagonal; heuristic verification only','samples':samples,'maximumAbsoluteDelta':max(abs(s['deltaY']) for s in samples if s['deltaY'] is not None)}}
write(z/'qa/repair-r09_c05-v3-row-agent-mechanical-audit.json',result)
print(json.dumps({'roadEdgeSamples':samples,'maxEdgeDelta':result['roadEdgeSampling']['maximumAbsoluteDelta'],'repairPixels':[{'id':x['id'],'count':x['repairPixelCount']} for x in reports]}))

