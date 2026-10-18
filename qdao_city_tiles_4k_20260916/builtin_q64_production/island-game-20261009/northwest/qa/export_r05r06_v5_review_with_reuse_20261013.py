from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as c
r=c.r
M=Z/'qa/connected-r05-r06-current-v5.manifest.json';O=Z/'qa/r05r06_v5_changed_native_review_20261013';O.mkdir(exist_ok=False)
tiles,origin=c.load_manifest(M);imgs={}
for t in tiles:
 assert r.file_info(Path(t['image']['path']))==t['image'];assert r.file_info(Path(t['record']['path']))==t['record']
 imgs[t['tileId']]=np.array(Image.open(t['image']['path']).convert('RGB'))
def crop(box):
 out=np.empty((box[3]-box[1],box[2]-box[0],3),np.uint8);cover=np.zeros(out.shape[:2],np.uint8)
 for t in tiles:
  ox,oy=t['clusterOffset'];x0,y0=max(ox,box[0]),max(oy,box[1]);x1,y1=min(ox+4096,box[2]),min(oy+4096,box[3])
  if x1<=x0 or y1<=y0:continue
  out[y0-box[1]:y1-box[1],x0-box[0]:x1-box[0]]=imgs[t['tileId']][y0-oy:y1-oy,x0-ox:x1-ox]
  cover[y0-box[1]:y1-box[1],x0-box[0]:x1-box[0]]+=1
 assert (cover==1).all()
 return out
priorp=Z/'qa/r05r06_v1_native17_connected_continuation_review_20261013.json';prior=r.read_json(priorp);items=[]
for q in prior['items']:
 px=crop(q['box']);oldp=Path(q['image']['path']);assert r.file_info(oldp)==q['image']
 unchanged=np.array_equal(px,np.array(Image.open(oldp).convert('RGB')))
 if unchanged:
  assert q['geometry']=='pass'
  result=dict(name=oldp.stem,box=q['box'],output=q['image'],geometry='PASS',method='Exact pixel comparison; reuse prior native geometry PASS',reuseRecord=r.file_info(priorp))
 else:
  p=O/oldp.name;Image.fromarray(px).save(p);result=dict(name=oldp.stem,box=q['box'],output=r.file_info(p),geometry='PENDING_NATIVE_VIEW',method='changed native crop')
 items.append(result)
extra={
 'ground_left_margin':[3550,5350,4000,6604],
 'ground_right_margin':[4600,5350,5004,6604],
 'ground_top_margin':[3650,5190,4904,5680],
 'ground_bottom_margin':[3650,6310,4904,6764],
 'paving_left_margin':[4480,4000,4930,4900],
 'paving_left_top_margin':[4650,3770,5470,4250],
 'paving_left_right_margin':[5280,4000,5650,4765],
 'paving_left_bottom_margin':[4650,4550,5470,4965]
}
extras=[]
for name,box in extra.items():
 p=O/f'{name}.png';px=crop(box);Image.fromarray(px).save(p);extras.append(dict(name=name,box=box,output=r.file_info(p),nativeSize=[px.shape[1],px.shape[0]],geometry='PENDING_NATIVE_VIEW'))
checks=[]
for tid,base in [('r06_c03','tiles/r06_c03_candidate-v7_4096.png'),('r06_c04','tiles/r06_c04_rail-east-mid-v1_4096.png')]:
 old=np.array(Image.open(Z/base).convert('RGB'));new=imgs[tid];n=int(np.any(old[-115:]!=new[-115:],axis=2).sum())
 checks.append(dict(tileId=tid,base=r.file_info(Z/base),south115Unchanged=(n==0),changedPixels=n))
data=dict(operation='exact native diagnostic crops with unchanged PASS reuse',isAiGeneration=False,resizing=False,manifest=r.file_info(M),priorReview=r.file_info(priorp),items=items,extraBoundaryCrops=extras,anchorChecks=checks)
c.write_json(O/'index.json',data)
print(json.dumps(dict(index=r.file_info(O/'index.json'),changed=[x['name'] for x in items if x['geometry']!='PASS'],reused=sum(x['geometry']=='PASS' for x in items),extra=len(extras),anchorChecks=checks)))

