from pathlib import Path
import json,hashlib,re
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
native=list((Z/'native').glob('*.png')); coords={}
for p in native:
 m=re.fullmatch(r'(r\d{2}_c\d{2})_s(\d{2}_\d{2})_a\d+\.png',p.name)
 if m: coords.setdefault(m[1],set()).add(m[2])
tiles=sorted({p.name[:7] for p in (Z/'tiles').glob('r??_c??_candidate-*_4096.png')})
passed=['r03_c02','r03_c03','r03_c04','r04_c03','r04_c04','r05_c03','r05_c04']
def rd(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Z/'progress.json'; d=rd(p)
d.update(updatedAtUtc=now,status='actual_generation_and_connected_repair_continuing',generatedNativeCount=len(native),candidateCoordinateCount=sum(map(len,coords.values())),assembledCandidateTileCount=len(tiles),fullyCovered4kCount=sum(len(x)==16 for x in coords.values()),internalPassed4kCount=7,usableNativeCount=112,formalAcceptedCount=0,complete4kCount=0,currentTile='r06_c03',currentPatch='r06_c03_s01_03_a01',latest4kCandidate='tiles/r05_c03_candidate-v8_4096.png',generationHold=False,nextStep='Continue r06c03, r06c04 and r04c02; repair four-tile lantern in r04/r05 connected group.',internalPassMeaning='Seven candidates have all internal standard seam crops passed; shared seams or outer perimeter pending. No whole-zone completion.')
save(p,d)
p=Z/'local-continuation-20261011.json';d=rd(p);d.update(updatedAtUtc=now,candidateTileIds=tiles,candidateTileCount=len(tiles),internalPassedTileIds=passed,activeAssignments={'root':'r06_c03','right_completion':'r06_c04','west_closure':'r04_c02','connected_closure':'r04/r05 c03/c04 shared-seam repairs'},missingNativeCoordinates={f'r{r:02d}_c{c:02d}':[f's{sr:02d}_{sc:02d}' for sr in range(1,5) for sc in range(1,5) if f'{sr:02d}_{sc:02d}' not in coords.get(f'r{r:02d}_c{c:02d}',set())] for r in range(1,8) for c in range(1,8)})
save(p,d)
p=Z/'continuation-round-20261011.json';d=rd(p);d.update(updatedAtUtc=now,candidateTileCount=len(tiles),internalPassed4kCount=7,formalAcceptedCount=0,currentStage='r06 generation and r04/r05 connected repair');save(p,d)
print(json.dumps({'nativePngs':len(native),'coordinates':sum(map(len,coords.values())),'fullCandidates':len(tiles),'internalPassed':7,'formalAccepted':0}))
