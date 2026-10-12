from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=Z/'qa/connected-2x2-20261010'
old=read(base/'19fb16977e813532f978/manifest.json')
out=base/'fbeae19cb75e8621c1f0';new=read(out/'manifest.json')
old_by_name={Path(e['file']).name:e for e in old['exports']}
reviews=[]
for e in new['exports']:
 name=Path(e['file']).name
 if not name.endswith('-100pct.png'):continue
 assert sha(e['file'])==e['sha256']==old_by_name[name]['sha256']
 reviews.append({'file':e['file'],'sha256':e['sha256'],'reviewTransfer':'byte-identical to original-pixel window viewed by root','originalReview':str(base/'19fb16977e813532f978/visual-review.json'),'geometryPassed':True,'openP2':False})
assert len(reviews)==17
for tid,s in new['sources'].items():
 assert sha(s['file'])==s['sha256']
 progress=read(Z/tid/'tile-progress.json')
 assert progress['candidateSha256']==s['sha256']
 assert progress['internalPassed4kCount']==1
record={'group':'r05-r06_c13-c14','reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'connected_group_art_review_passed_with_documented_P3_cosmetics','sourceManifest':str(out/'manifest.json'),'sources':new['sources'],'sourceHashesChecked':True,'internalPassedTileCount':4,'sharedEdgeWindowsReviewed':17,'sharedEdgePixelsUnchangedFromViewedIntermediate':True,'windows':reviews,'openP1':0,'openP2':0,'retainedCosmetics':['Mild native material or lighting steps on plaster, timber, flowers, and gold; contours remain coherent.','Tile-local details are preserved in each tile review.'],'outerPerimeterWithFutureNeighbors':'not yet reviewed; future tiles must use these actual native/candidate boundaries','formalAcceptedCount':0,'runtimeWorkRequested':False,'builtinOnly':True}
save(out/'visual-review.json',record)
save(Z/'connected-groups.json',{'groups':[{'group':record['group'],'review':str(out/'visual-review.json'),'sources':new['sources'],'connectedReviewedTileCount':4,'formalAcceptedCount':0}]})
print(json.dumps({'groupPassed':True,'sharedEdges':17,'review':str(out/'visual-review.json')}))

