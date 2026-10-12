from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
Q=T/'qa/core-baseline/31b09711d96a1bf993b7'
R=T/'qa/local-repair-resume2-20261013'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((T/'qa/model-hold-20261013/partial-native-review.json').read_text(encoding='utf-8'))
reuse=[]
for a in old['seams']+old['reviewedCompleteIntersections']:
 new=Q/Path(a['file']).name
 assert sha(new)==a['sha256']
 reuse.append({'file':str(new),'sha256':sha(new),'priorStatus':a['status'],'priorReport':str(T/'qa/model-hold-20261013/partial-native-review.json'),'evidenceReused':True})
issues={
 'vertical-p11-p12-join-100pct.png':[],
 'vertical-p12-p13-join-100pct.png':['fascia'],
 'vertical-p13-p14-join-100pct.png':[],
 'vertical-p21-p22-join-100pct.png':['wallrail'],
 'vertical-p22-p23-join-100pct.png':['fascia'],
 'vertical-p23-p24-join-100pct.png':[],
 'horizontal-p11-p21-join-100pct.png':[],
 'horizontal-p12-p22-join-100pct.png':['upperroof'],
 'horizontal-p13-p23-join-100pct.png':['fascia'],
 'horizontal-p14-p24-join-100pct.png':[],
 'horizontal-p22-p32-join-100pct.png':['wallrail'],
 'horizontal-p23-p33-join-100pct.png':['trunk'],
 'horizontal-p24-p34-join-100pct.png':[],
 'intersection-r1-c1-100pct.png':['upperroof'],
 'intersection-r1-c2-100pct.png':['fascia'],
 'intersection-r1-c3-100pct.png':[],
 'intersection-r2-c1-100pct.png':['wallrail'],
 'intersection-r2-c2-100pct.png':['wallrail'],
 'intersection-r2-c3-100pct.png':['trunk'],
}
new=[{'file':str(Q/n),'sha256':sha(Q/n),'viewedAtNativeScale':True,'issueIds':v,'status':'P2-pending' if v else 'no-new-P2'} for n,v in issues.items()]
report={'tile':'r06_c15','createdAt':datetime.now(timezone.utc).isoformat(),'candidate':str(Q/'r06_c15-core-baseline.candidate.png'),'candidateSha256':sha(Q/'r06_c15-core-baseline.candidate.png'),'sourceInputSignature':'31b09711d96a1bf993b76aede0f41ee8df10a9159ae715ab03414bfb5692dd50','totalSeams':24,'totalCorners':9,'reusedWindows':reuse,'newlyViewedWindows':new,'pendingIssueIds':['panel','ledge','roof','trunk','wallrail','fascia','upperroof'],'pendingIssueCount':7,'internalPassed4kCount':0,'formalAcceptedCount':0,'upperroofFinding':'Diagonal roof ribs have small positional phase breaks along y1024 at x approximately 950..1600; separate from lower roof defect.'}
(R/'baseline-review-v1.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'seamsTotal':24,'cornersTotal':9,'reusedWindows':len(reuse),'newlyViewedWindows':len(new),'pendingIssueCount':7}))
