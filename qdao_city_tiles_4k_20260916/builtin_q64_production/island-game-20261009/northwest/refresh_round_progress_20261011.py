from pathlib import Path
import re,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
native=list((Z/'native').glob('*.png')); coords={}
for p in native:
 m=re.fullmatch(r'(r\d{2}_c\d{2})_s(\d{2}_\d{2})_a\d+\.png',p.name)
 if m: coords.setdefault(m[1],set()).add(m[2])
tiles=sorted({p.name[:7] for p in (Z/'tiles').glob('r??_c??_candidate-*_4096.png')})
now=datetime.now(timezone.utc).isoformat()
p=Z/'progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d.update(status='actual_generation_and_internal_repair_continuing',updatedAtUtc=now,generatedNativeCount=len(native),candidateCoordinateCount=sum(map(len,coords.values())),assembledCandidateTileCount=len(tiles),fullyCovered4kCount=sum(len(x)==16 for x in coords.values()),internalPassed4kCount=5,usableNativeCount=80,formalAcceptedCount=0,complete4kCount=0,currentTile='r05_c03',currentPatch='r05_c03_paving_join_repair_a01',latest4kCandidate='tiles/r05_c03_candidate-v5_4096.png',generationHold=False,nextStep='Finish r05c03 and r05c04 internal defects, connect r04/r05 group with whole lantern repair; continue r04c02 and remaining northwest tiles.',candidateCountMeaning='Unique formal coordinates with native coverage; raw count includes rejected attempts and local repairs. No whole-zone completion.',internalPassMeaning='r03c02v7 and r03/04 c03/04 four tiles have internal closure. First 2x2 shared seams also passed; perimeter pending.',connectedClusterCount=1,connectedInternalSeamsPassed=17,externalPassed4kCount=0,firstOutputThisRound={'path':'native/r05_c03_stair_right_repair_a02.png','sha256':hashlib.sha256((Z/'native/r05_c03_stair_right_repair_a02.png').read_bytes()).hexdigest()},gitOperationsDelegated=True)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap={'updatedAtUtc':now,'target4kCount':49,'candidateTileIds':tiles,'candidateTileCount':len(tiles),'internalPassedTileIds':['r03_c02','r03_c03','r03_c04','r04_c03','r04_c04'],'formalAcceptedTileCount':0,'connectedClusterManifest':'qa/connected-closure-current-v5.manifest.json','missingNativeCoordinates':{f'r{r:02d}_c{c:02d}':[f's{sr:02d}_{sc:02d}' for sr in range(1,5) for sc in range(1,5) if f'{sr:02d}_{sc:02d}' not in coords.get(f'r{r:02d}_c{c:02d}',set())] for r in range(1,8) for c in range(1,8)},'networkStatus':'root original builtin produced actual output after reported agent interruption','runtimeInScope':False,'gitOperationsDelegated':True}
(Z/'local-continuation-20261011.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'nativePngs':len(native),'coordinates':sum(map(len,coords.values())),'fullCandidates':len(tiles),'internalPassed':5}))
