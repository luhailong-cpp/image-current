from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
p=Z/'r12_c08/native/p41-v1.png'
tiles=[]
for sp in sorted(Z.glob('r??_c??/selected-patches.json')):
 s=read(sp);tiles.append(dict(tile=sp.parent.name,selection=str(sp),selectedPositions=len(s.get('patches',{})),internalReady=s.get('internalReady',False),candidate=s.get('candidate'),formalAccepted=s.get('formalAccepted',False)))
d=dict(resumedAt=now,currentCoordinate='r12_c08/p41',firstActualOutput=dict(file=str(p),sha256=sha(p),receipt=str(Z/'r12_c08/p41-v1.receipt.json'),builtin=True,actualModel=None,actualQuality=None),candidateCount=sum(t['selectedPositions']==16 for t in tiles),internalPassedCount=sum(t['internalReady'] for t in tiles),formalAcceptedCount=sum(t['formalAccepted'] for t in tiles),tiles=tiles,externalPending='All formal acceptance remains pending complete available-neighbor checks; G2 r10c08/c09 deck geometry, C2 r10c08 north adoption shadow, r12c08 p14 railing are known open',next='Generate r12c08 p42/p43/p44; finish p14 rail candidate; review24+9 and neighbor edges. Other columns resume from saved files.',errors=['Subagents reported network permission revoked and one401 before this successful root builtin output. No alternate entry point used.'],gitPolicy='No git/index/ref/commit/push or migration directory mutations; centralized migration owns Git',all49Complete=False)
(Z/'continuation-round-20261011.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:d[k] for k in ('candidateCount','internalPassedCount','formalAcceptedCount','currentCoordinate')}))

