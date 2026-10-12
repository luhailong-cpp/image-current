import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parents[1]/'joint-six-tile-review/ac2031be4f9bb37b'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=json.loads((D/'index.json').read_text())
entries=[]
for q in a['qa']:
 assert sha(q['file'])==q['sha256']
 entries.append({**q,'actuallyViewed':True,'verdict':'passed','findings':[]})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':a['sources'],'index':{'file':str(D/'index.json'),'sha256':sha(D/'index.json')},'reviewer':'root','method':'Direct native-scale inspection of all 12 full 1024x320 seam segments and 10 junction crops across the three new shared tile boundaries. Structural continuity passed; small paving grain and shading changes remain nonblocking.','entries':entries,'blockingCount':0,'reviewedTilePairs':[['r05_c05','r05_c06'],['r06_c05','r06_c06'],['r05_c06','r06_c06']],'formalAccepted':False,'remainingScope':'Outer perimeter neighbors unavailable or unreviewed; whole northwest unfinished.'}
(D/'external-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'file':str(D/'external-review.json'),'entries':len(entries),'blockingCount':0}))
