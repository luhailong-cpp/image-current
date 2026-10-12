"""Join the next r05/r06 neighborhood; preserve the accepted r05 shared edge."""
from pathlib import Path
import json,argparse,numpy as np
import run_cross_with_strict_memo as memo
c=memo.connected;r=memo.r
original=c.join_pair
calls=0
def preserve_first_join(first,second,first_ids,second_ids,axis):
 global calls
 calls+=1
 if calls!=1:return original(first,second,first_ids,second_ids,axis)
 c.require(axis==1 and first.shape==second.shape==(c.PADDED,c.PADDED,3),'First join must be the exact accepted top row.')
 start=c.CORE+c.HALO
 out=np.empty((c.PADDED,c.PADDED_CLUSTER,3),np.uint8)
 labels=np.empty((c.PADDED,c.PADDED_CLUSTER),np.uint8)
 out[:,:start]=first[:,:start];out[:,start:]=second[:,c.HALO:]
 labels[:,:start]=first_ids[:,:start];labels[:,start:]=second_ids[:,c.HALO:]
 return out,labels,dict(axis=1,overlapPath=[c.HALO]*c.PADDED,statistics=dict(selectionPolicy='fixed native core boundary preserves independently reviewed r05 c03/c04 shared edge',minimumErrorPathUsed=False,preservedBoundary=4096))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);ap.add_argument('--output-dir',required=True);a=ap.parse_args()
 mp=Path(a.manifest).resolve();m=r.read_json(mp);policy=m.get('preservedPriorSharedBoundary',{})
 prior=r.pinned(policy.get('manifest'),mp.parent,'prior accepted manifest')
 closure=r.pinned(policy.get('closure'),mp.parent,'prior shared-boundary visual closure')
 pd=r.read_json(Path(prior['path']));cl=r.read_json(Path(closure['path']))
 r.require(cl.get('nativeQaPassed')==17 and cl.get('status')=='shared_boundary_visual_closure_passed_perimeter_pending','Prior shared edge has no visual closure.')
 for idx,tid in enumerate(('r05_c03','r05_c04')):
  old=next(t for t in pd['tiles'] if t['tileId']==tid)
  r.require(m['tileMatrix'][0][idx]==old,'Pinned accepted r05 tile changed.')
 r.require(policy.get('wrapper')==r.file_info(Path(__file__).resolve()),'Wrapper hash mismatch.')
 c.join_pair=preserve_first_join;c.build(mp,Path(a.output_dir).resolve())
 print(json.dumps({'strictInvocationMemo':memo.stats,'preservedPriorSharedBoundary':policy}))
if __name__=='__main__':main()
