from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
Q=T/'qa/full-native-resume-20261013-v1'
OLD=T/'qa/fourteen-native-resume-20261013-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
sp=T/'selected-patches.json';s=read(sp);m=read(Q/'manifest.json')
a=np.asarray(Image.open(Q/'candidate-4096.png').convert('RGB'))
assert a.shape==(4096,4096,3) and len(s['patches'])==16
for v in m['sources']:
 p=T/s['patches'][v['patch']];assert sha(p)==v['sha256']
 n=np.asarray(Image.open(p).convert('RGB'));x,y=v['destination']
 assert n.shape==(1254,1254,3) and np.array_equal(a[y:y+1024,x:x+1024],n[115:1139,115:1139])
old={e['sha256'] for e in read(OLD/'root-native-review.json')['evidence']}
evidence=[]
for e in m['evidence']:
 assert sha(e['file'])==e['sha256']
 evidence.append(dict(file=e['file'],sha256=e['sha256'],review='reused identical 14-patch review evidence' if e['sha256'] in old else 'fresh original-resolution visual inspection; continuous caustic endpoints and facets'))
assert len(evidence)==33 and sum(e['sha256'] in old for e in evidence)==27
rp=Q/'root-native-geometry-review.json'
write_new(rp,dict(createdAt=datetime.now(timezone.utc).isoformat(),geometryPassed=True,reviewedSeams=24,reviewedCrossings=9,reusedEvidenceCount=27,newEvidenceCount=6,exact4096CoreReplay=True,evidence=evidence,materialStatus='Geometry and texture continuity inspected; minor hue variation proceeds to bounded color review',internalReady=False,formalAccepted=False))
write_new(T/'qa/selection-before-color-registration-20261013.json',s)
s.update(candidate=str(Q/'candidate-4096.png'),candidateSha256=sha(Q/'candidate-4096.png'),geometryReview=str(rp),status='full_native_geometry_passed_color_review_pending',internalReady=False,formalAccepted=False,materialPending=True)
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
write_new(T/'native-selected-before-color-20261013.json',s)
src=T.parent/'r13_c08/color_match_tile_resume_v2_20261012.py'
code=src.read_text(encoding='utf-8-sig').replace('native-selected-before-color-v2.json','native-selected-before-color-20261013.json').replace('resume-20261012-v2','resume-20261013-v1').replace('r13_c08','r14_c08')
dest=T/'color_match_tile_resume_20261013.py';assert not dest.exists();dest.write_text(code,encoding='utf-8')
print(json.dumps(dict(geometryEvidence=33,exactReplay=True,colorScript=str(dest))))
