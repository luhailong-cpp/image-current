"""Reuse this turn's immutable passed cluster check for crop preparation only.

The ordinary cross apply validator remains unchanged and still replays the
base/input/source/mask. No generated pixels, resize, registration or painting.
"""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as c
r=c.r
M=Z/'qa/connected-r05-r06-current-v1.manifest.json'
C=Z/'tiles/connected-r05-r06-cross-v1/connected-cluster.json'
expected='07349252a67c0381aaad659cc65cd5311a61151916bb20624ef60e4dcc9716f9'
assert r.file_info(C)['sha256']==expected
cluster=r.read_json(C);verification=cluster['verification']
assert verification['pixelCount']==8192*8192 and verification['allOutputPixelsExactlyMatchSameCoordinateVerifiedPaddedSource'] is True and verification['unassignedPixels']==0
pins=[r.file_info(C)]
for key in ('manifest','sourceIndexPlane'):
 pins.append(r.pinned(cluster[key],C.parent,key))
for source in cluster['sources']:
 assert source['coreValidation']['fullNativeCoverage'] is True
 for key in ('image','record'):pins.append(r.pinned(source[key],C.parent,'unchanged direct verified source'))
tiles,origin=c.load_manifest(M)
for i,tile in enumerate(tiles):
 item=cluster['outputs'][i]
 assert tile['tileId']==item['tileId'] and tile['image']==r.pinned(item['output'],C.parent,'verified output')
 rec=r.read_json(Path(tile['record']['path']))
 assert rec['sourceId']==i and r.pinned(rec['cluster'],C.parent,'cluster projection')==r.file_info(C)
 assert rec['coverageAssertions']['fullNativeCoverage'] is True
 pins += [tile['image'],tile['record']]

def prepared_context(manifest_path,box,seen=None):
 assert manifest_path==M and r.file_info(M)==manifest_info
 box=c.validate_box(box);parts=c.intersections(tiles,box)
 crop=np.empty((1254,1254,3),np.uint8);coverage=np.zeros((1254,1254),np.uint8)
 for part in parts:
  tile=next(t for t in tiles if t['tileId']==part['tileId'])
  assert r.file_info(Path(tile['image']['path']))==tile['image']
  x0,y0,x1,y1=part['repairBox']
  with Image.open(tile['image']['path']) as im:crop[y0:y1,x0:x1]=np.array(im.convert('RGB').crop(part['tileBox']))
  coverage[y0:y1,x0:x1]+=1
 assert np.all(coverage==1)
 return crop,dict(manifest=manifest_info,tiles=tiles,clusterOrigin=origin,cropBox=box,globalBox=[box[i]+origin[i%2] for i in range(4)],parts=parts),{}

manifest_info=r.file_info(M)
c.canonical_context=prepared_context
jobs=[('cross_r06_c03c04_rail_west_a01',[3470,4596,4724,5850],'exact native cross-boundary railing target; align cap and consolidate wall foot without moving any column'),('cross_r05r06_c04_paving_north_a01',[5060,3470,6314,4724],'exact native north south boundary paving target; join the interrupted diagonal grout without moving wall or tree shadows')]
results=[]
for stem,box,role in jobs:
 # Strict preparation may have completed while the reuse helper was queued.
 ip=Z/'guides'/f'{stem}.input.json'
 if ip.exists():
  data=r.read_json(ip);assert data['manifest']==manifest_info and data['cropBox']==box
  results.append(dict(stem=stem,status='already_prepared_by_ongoing_strict_validator',input=r.file_info(ip)))
 else:results.append(dict(stem=stem,status='prepared_from_passed_unchanged_cluster',result=c.prepare(M,box,stem,Z/'qa/cross_r04r05_standard_references-v1.json',role)))
out=Z/'qa/r05r06_prepare_passed_check_reuse_20261013_v1.json'
c.write_json(out,dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),operation='reuse passed unchanged cluster verification for exact crop preparation',verification=verification,unchangedHashPins=pins,manifest=manifest_info,script=r.file_info(Path(__file__)),finalApplyValidatorUnchanged=True,results=results))
print(json.dumps(dict(evidence=r.file_info(out),prepared=[j[0] for j in jobs])))
