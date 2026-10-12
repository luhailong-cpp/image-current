"""Carry a review only across independently verified byte-identical windows."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
HERE=Path(__file__).resolve().parent;ZONE=HERE.parents[2]
ORIGINAL=HERE.parent/'19fb16977e813532f978'
PREVIOUS=HERE.parent/'fbeae19cb75e8621c1f0'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=read(HERE/'manifest.json');original=read(ORIGINAL/'manifest.json');review=read(ORIGINAL/'visual-review.json')
new={Path(x['file']).name:x for x in manifest['exports'] if x['file'].endswith('-100pct.png')}
old={Path(x['file']).name:x for x in original['exports'] if x['file'].endswith('-100pct.png')}
viewed={Path(x['file']).name:x for x in review['items']}
assert len(new)==len(old)==len(viewed)==17 and set(new)==set(old)==set(viewed)
windows=[]
for name,item in new.items():
    former=old[name];assert sha(item['file'])==item['sha256']==former['sha256']==sha(former['file']),name
    assert viewed[name]['reviewedAtNativeScale'] and viewed[name]['structuralContinuity']=='passed' and not viewed[name]['priority2Issue']
    windows.append({'file':item['file'],'sha256':item['sha256'],'originalFile':former['file'],'originalSha256':former['sha256'],'reviewTransfer':'byte-identical to original-pixel window viewed by root','originalReview':str(ORIGINAL/'visual-review.json'),'geometryPassed':True,'openP2':False})
internal=[]
for tid,source in manifest['sources'].items():
    assert sha(source['file'])==source['sha256']
    p=ZONE/tid/'tile-progress.json';data=read(p)
    assert data['internalPassed4kCount']==1 and data['candidateSha256']==source['sha256'] and data['formalAcceptedCount']==0
    internal.append({'tile':tid,'candidateSha256':source['sha256'],'internalPassed':True,'sourceRecord':str(p),'sourceRecordSha256':sha(p)})
prior=read(PREVIOUS/'visual-review.json')
result=copy.deepcopy(prior)
result.update({'reviewedAt':datetime.now(timezone.utc).isoformat(),'sourceManifest':str(HERE/'manifest.json'),'sources':manifest['sources'],'windows':windows,'sourceHashesChecked':True,'sharedEdgePixelsUnchangedFromViewedIntermediate':True,'internalPassedTileCount':4,'internalTileRecords':internal,'sharedEdgeWindowsReviewed':17,'originalVisualReview':{'file':str(ORIGINAL/'visual-review.json'),'sha256':sha(ORIGINAL/'visual-review.json')},'previousGroupReview':{'file':str(PREVIOUS/'visual-review.json'),'sha256':sha(PREVIOUS/'visual-review.json')},'reviewMethod':'SHA256 of all 17 re-exported native windows matches both the original viewed PNG bytes and original manifest. Prior visual findings transfer unchanged; no new visual pass is claimed.','snapshotReason':'r06_c13 south gold cap added outside the 17 current group seam windows; its separate local review is retained.','southCapReview':str(ZONE/'r06_c13/qa/r07-p14-north-cap-20261010/visual-review.json'),'formalAcceptedCount':0})
save(HERE/'visual-review.json',result)
groupfile=ZONE/'connected-groups.json';before=groupfile.read_bytes();groups=json.loads(before)
backup=HERE/'connected-groups-before.json';assert not backup.exists();backup.write_bytes(before)
matches=[g for g in groups['groups'] if g['group']=='r05-r06_c13-c14'];assert len(matches)==1
group=matches[0];group.update({'review':str(HERE/'visual-review.json'),'reviewSha256':sha(HERE/'visual-review.json'),'sourceManifest':str(HERE/'manifest.json'),'sourceSignature':manifest['signature'],'sources':manifest['sources'],'connectedReviewedTileCount':4,'internalPassedTileCount':4,'sharedEdgeWindowsReviewed':17,'originalReview':str(ORIGINAL/'visual-review.json'),'previousReview':str(PREVIOUS/'visual-review.json'),'formalAcceptedCount':0})
assert groupfile.read_bytes()==before,'shared group record changed concurrently'
save(groupfile,groups)
save(HERE/'snapshot-verification.json',{'signature':manifest['signature'],'nativeWindowsCompared':17,'byteIdenticalWindowCount':17,'currentSourceHashes':{k:v['sha256'] for k,v in manifest['sources'].items()},'internalPassedTileCount':4,'formalAcceptedCount':0,'groupFileSha256':sha(groupfile),'updatedSharedFile':str(groupfile),'progressOrQueueModified':False})
print(json.dumps({'signature':manifest['signature'],'identicalNativeWindows':17,'internalPassedTiles':4,'formalAcceptedCount':0}))
