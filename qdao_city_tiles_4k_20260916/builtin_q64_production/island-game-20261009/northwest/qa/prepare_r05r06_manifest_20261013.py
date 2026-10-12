from pathlib import Path
import json,hashlib,argparse
Z=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
for n in ('r06c04-image','r06c04-record','output'):ap.add_argument('--'+n,required=True)
a=ap.parse_args()
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
prior=Z/'qa/connected-r04-r05-current-v5.manifest.json';pd=json.loads(prior.read_text())
top=[next(t for t in pd['tiles'] if t['tileId']==tid) for tid in ('r05_c03','r05_c04')]
cl=json.loads((Z/'qa/r06_c03_v7_internal_closure_20261012/closure.json').read_text())
bottom=[dict(tileId='r06_c03',image=cl['base'],record=cl['record']),dict(tileId='r06_c04',image=info(Path(a.r06c04_image)),record=info(Path(a.r06c04_record)))]
for t in top+bottom:
 for key in ('image','record'):assert info(Path(t[key]['path']))==t[key]
m=dict(schemaVersion=1,tileMatrix=[top,bottom],preservedPriorSharedBoundary=dict(manifest=info(prior),closure=info(Z/'qa/connected-r04-r05-final-v1/closure.json'),wrapper=info(Z/'qa/build_r05r06_preserving_prior_20261013.py'),policy='Accepted r05 shared vertical edge stays exact at native core boundary; new r06 and r05/r06 joins use existing same-coordinate DP.'))
with Path(a.output).open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)
print(json.dumps(info(Path(a.output))))
