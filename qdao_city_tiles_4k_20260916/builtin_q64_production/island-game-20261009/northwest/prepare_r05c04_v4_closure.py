from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from assemble_tile import save_qa
Z=Path(__file__).resolve().parent
out=Z/'qa/r05_c04_v4_internal_closure'
assert not out.exists()
out.mkdir()
base=Image.open(Z/'tiles/r05_c04_candidate-v1_4096.png').convert('RGB')
final=Image.open(Z/'tiles/r05_c04_candidate-v4_4096.png').convert('RGB')
qa=save_qa(out,final)
old=json.loads((Z/'qa/assembly_r05_c04_candidate-v1_4096/qa_index.json').read_text())
for i,(new,prior) in enumerate(zip(qa['seamAndJunctionCrops'],old['seamAndJunctionCrops'])):
 new['equalsPreviouslyReviewedV1Crop']=bool(np.array_equal(np.array(Image.open(new['path'])),np.array(Image.open(prior['path']))))
 new['index']=i
repairs=[]
for name,box in [('upper_paving',(2600,100,3854,1354)),('lower_left',(0,2842,1254,4096)),('bottom_seam',(600,2842,1854,4096))]:
 p=out/(name+'_final_100pct.png');final.crop(box).save(p);repairs.append({'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tileCropBox':list(box),'nativeScale100Percent':True})
a,b=np.array(base),np.array(final)
edges={}
for name,aa,bb in [('north',a[0],b[0]),('south',a[-1],b[-1]),('west',a[:,0],b[:,0]),('east',a[:,-1],b[:,-1])]:
 ids=np.flatnonzero(np.any(aa!=bb,axis=1));edges[name]={'changedPixelCount':int(ids.size),'indexMinMax':None if not ids.size else [int(ids.min()),int(ids.max())]}
d={'schemaVersion':1,'tileId':'r05_c04','status':'final_native_visual_review_pending','image':{'path':(Z/'tiles/r05_c04_candidate-v4_4096.png').as_posix(),'sha256':hashlib.sha256((Z/'tiles/r05_c04_candidate-v4_4096.png').read_bytes()).hexdigest()},'provenance':{'path':(Z/'tiles/r05_c04_candidate-v4_4096.native-repair.json').as_posix(),'sha256':hashlib.sha256((Z/'tiles/r05_c04_candidate-v4_4096.native-repair.json').read_bytes()).hexdigest()},'qa':qa,'repairCrops':repairs,'outerEdgeChangesVsV1':edges,'formalAccepted':False,'externalSeamsAccepted':False}
(out/'qa_index.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'changedCropIndexes':[e['index'] for e in qa['seamAndJunctionCrops'] if not e['equalsPreviouslyReviewedV1Crop']],'edges':edges,'image':d['image'],'provenance':d['provenance']}))
