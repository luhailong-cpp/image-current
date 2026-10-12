from pathlib import Path
import sys,json,argparse,copy,numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as c
r=c.r
ap=argparse.ArgumentParser()
for n in ('manifest','operation','output'):ap.add_argument('--'+n,required=True)
for n in ('rebase-input','rebased-output','rebased-derivation'):ap.add_argument('--'+n)
a=ap.parse_args();p=lambda s:(Z/s).resolve()
mp,op,out=map(p,(a.manifest,a.operation,a.output));m=r.read_json(mp);o=r.read_json(op)
assert o['manifest']==r.file_info(mp) and o['operation']==c.OPERATION
updated={x['tileId']:dict(tileId=x['tileId'],image=x['image'],record=r.file_info(Path(x['projectionRecordPath']))) for x in o['outputs']}
nm=dict(schemaVersion=1,tiles=[updated.get(t['tileId'],t) for t in m['tiles']])
for t in nm['tiles']:
 for k in ('image','record'):assert r.file_info(Path(t[k]['path']))==t[k]
c.write_json(out,nm)
result=dict(manifest=r.file_info(out))
if a.rebase_input:
 oldp,ip,dp=map(p,(a.rebase_input,a.rebased_output,a.rebased_derivation));old=r.read_json(oldp)
 tiles,origin=c.load_manifest(out);box=old['cropBox'];parts=c.intersections(tiles,box)
 crop=np.empty((1254,1254,3),np.uint8);coverage=np.zeros((1254,1254),np.uint8)
 for part in parts:
  t=next(x for x in tiles if x['tileId']==part['tileId']);x0,y0,x1,y1=part['repairBox']
  with Image.open(t['image']['path']) as im:crop[y0:y1,x0:x1]=np.array(im.convert('RGB').crop(part['tileBox']))
  coverage[y0:y1,x0:x1]+=1
 assert np.all(coverage==1)
 target=old['editTarget'];assert r.file_info(Path(target['path']))=={k:target[k] for k in ('path','sha256')}
 with Image.open(target['path']) as im:assert np.array_equal(crop,np.array(im.convert('RGB')))
 ctx=dict(manifest=r.file_info(out),tiles=tiles,clusterOrigin=origin,cropBox=box,globalBox=[box[i]+origin[i%2] for i in range(4)],parts=parts)
 note=dict(originalInput=r.file_info(oldp),originalManifest=old['manifest'],sameEditTargetBytes=True,pixelCountCompared=1254*1254,reason='Prior repair footprint is disjoint. The exact actual image submitted to builtin generation also equals the current pinned crop. No new generation or image mutation.')
 derived=r.read_json(Path(target['derivationRecord']['path']));derived.update(ctx);derived['unchangedTargetReuse']=note
 c.write_json(dp,derived)
 data=copy.deepcopy(old);data.update(ctx);data['editTarget']['derivationRecord']=r.file_info(dp);data['unchangedTargetReuse']=note
 c.write_json(ip,data);result.update(rebasedInput=r.file_info(ip),rebasedDerivation=r.file_info(dp))
print(json.dumps(result))
