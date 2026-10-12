from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
entries=[]
for id,box,roi in [('s02_04_laststubs06-expanded',[23437,25485,24691,26739],[0,0,1139,1254]),('s04_04_surfacefix01-core',[23437,27533,24691,28787],[115,115,1139,1139])]:
 native=id.rsplit('-',1)[0];p=r/('native/'+native+'.png');entries.append(dict(id=id,file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeWorldBox=box,sourceROI=roi,localReview=str(r/'qa/resume-full-qa-v06-20261013/review.json'),generationRecord=str(p.with_suffix('.png.generation.json')),reviewStatus='trial-pending-full-local-and-perimeter-review'))
(r/'candidate/native-roi-entries-v06.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
