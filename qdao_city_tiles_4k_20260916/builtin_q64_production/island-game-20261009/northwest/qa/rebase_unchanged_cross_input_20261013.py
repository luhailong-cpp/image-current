from pathlib import Path
import sys,json,argparse,copy
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as c
r=c.r
ap=argparse.ArgumentParser()
for n in ('manifest','input','output','derivation'):ap.add_argument('--'+n,required=True)
a=ap.parse_args();p=lambda s:(Z/s).resolve()
mp,oldp,out,dp=map(p,(a.manifest,a.input,a.output,a.derivation))
old=r.read_json(oldp);tiles,origin=c.load_manifest(mp);box=old['cropBox'];parts=c.intersections(tiles,box)
crop=np.empty((1254,1254,3),np.uint8);coverage=np.zeros((1254,1254),np.uint8)
for part in parts:
 t=next(x for x in tiles if x['tileId']==part['tileId'])
 assert r.file_info(Path(t['image']['path']))==t['image']
 assert r.file_info(Path(t['record']['path']))==t['record']
 x0,y0,x1,y1=part['repairBox']
 with Image.open(t['image']['path']) as im:crop[y0:y1,x0:x1]=np.array(im.convert('RGB').crop(part['tileBox']))
 coverage[y0:y1,x0:x1]+=1
assert np.all(coverage==1)
target=old['editTarget'];assert r.file_info(Path(target['path']))=={k:target[k] for k in ('path','sha256')}
with Image.open(target['path']) as im:assert np.array_equal(crop,np.array(im.convert('RGB')))
ctx=dict(manifest=r.file_info(mp),tiles=tiles,clusterOrigin=origin,cropBox=box,globalBox=[box[i]+origin[i%2] for i in range(4)],parts=parts)
note=dict(originalInput=r.file_info(oldp),originalManifest=old['manifest'],sameEditTargetBytes=True,pixelCountCompared=1254*1254,reason='Disjoint previous repair; exact actually submitted target is byte-equivalent to the current crop. Actual generation reference list preserved.')
derived=r.read_json(Path(target['derivationRecord']['path']));derived.update(ctx);derived['unchangedTargetReuse']=note;c.write_json(dp,derived)
data=copy.deepcopy(old);data.update(ctx);data['editTarget']['derivationRecord']=r.file_info(dp);data['unchangedTargetReuse']=note;c.write_json(out,data)
print(json.dumps(dict(input=r.file_info(out),derivation=r.file_info(dp))))

