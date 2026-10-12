from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Q=T/'qa/full-native-resume-20261012-v2';Q1=T/'qa/full-native-resume-20261012-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
sp=T/'selected-patches.json';s=json.loads(sp.read_text(encoding='utf-8-sig'));m=json.loads((Q/'manifest.json').read_text(encoding='utf-8-sig'))
can=Q/'candidate-4096.png';a=np.asarray(Image.open(can).convert('RGB'));assert a.shape==(4096,4096,3)
for v in m['sources']:
 p=T/s['patches'][v['patch']];assert p.resolve()==Path(v['file']).resolve() and sha(p)==v['sha256']
 n=np.asarray(Image.open(p).convert('RGB'));x,y=v['destination'];assert n.shape==(1254,1254,3) and np.array_equal(a[y:y+1024,x:x+1024],n[115:1139,115:1139])
fresh={'p14--p24','p23--p24','p24--p34','cross-r1-c3','cross-r2-c3'};e=[]
for p in sorted(Q.glob('*.png')):
 if p.name in ['candidate-4096.png','preview-QA-1024.png']:continue
 if p.stem not in fresh:assert sha(p)==sha(Q1/p.name)
 e.append(dict(file=str(p),sha256=sha(p),review='inspected fresh at native resolution' if p.stem in fresh else 'byte-identical evidence reused from native-v1 review'))
assert len(e)==33
rp=Q/'root-native-geometry-review.json';assert not rp.exists()
write(rp,dict(createdAt=datetime.now(timezone.utc).isoformat(),geometryPassed=True,materialStatus='p24-v2 removes straight water facet-density transition; mild hue difference remains for bounded color review',evidence=e,exact4096CoreReplay=True,internalReady=False,formalAccepted=False))
snapshot=T/'qa/selection-before-full-native-v2-registration-20261012.json';assert not snapshot.exists();snapshot.write_bytes(sp.read_bytes())
s.update(candidate=str(can),candidateSha256=sha(can),status='full_native_geometry_passed_color_review_pending',geometryReview=str(rp),internalReady=False,formalAccepted=False,materialPending=True);write(sp,s)
backup=T/'native-selected-before-color-v2.json';assert not backup.exists();backup.write_bytes(sp.read_bytes())
code=(T/'color_match_tile_resume_20261012.py').read_text(encoding='utf-8-sig').replace('native-selected-before-color.json','native-selected-before-color-v2.json').replace('resume-20261012-v1','resume-20261012-v2')
dest=T/'color_match_tile_resume_v2_20261012.py';assert not dest.exists();dest.write_text(code,encoding='utf-8')
print(json.dumps(dict(exactCoreReplay=True,geometryEvidence=33,freshEvidence=5,colorScript=str(dest))))
