from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/eleven-native-resume-20261012-v1';old=T/'qa/first-two-rows-resume-20261012-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
fresh={'p21--p31','p22--p32','p23--p33','p31--p32','p32--p33','cross-r2-c1','cross-r2-c2'};e=[]
for p in Q.glob('*.png'):
 if p.name in ['candidate-4096.png','preview-QA-1024.png']:continue
 if p.stem not in fresh:assert sha(p)==sha(old/p.name)
 e.append(dict(file=str(p),sha256=sha(p),review='fresh native visual review' if p.stem in fresh else 'byte-identical to previously reviewed first-two-rows evidence'))
assert len(e)==20
m=read(Q/'manifest.json');rp=Q/'root-native-review.json';assert not rp.exists()
write(rp,dict(createdAt=datetime.now(timezone.utc).isoformat(),tile='r14_c08',selectedPositions=11,reviewedSeams=15,reviewedCrossings=5,evidence=e,geometryPassed=True,materialStatus='caustic paths continuous; no rectangular conditioning bands in reviewed evidence; whole tile color review after remaining 5 patches',sources=m['sources'],missing=['p34','p41','p42','p43','p44'],internalReady=False,formalAccepted=False,partialPreviewIsDeliverable=False))
sp=T/'selected-patches.json';s=read(sp);s['partialGeometryReview']=str(rp);write(sp,s)
print(json.dumps(dict(selectedPositions=11,geometryEvidence=20,missing=5)))
