from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/north-glaze-material-01';m=json.loads((d/'derivation.json').read_text());north=Path(m['actualNorthNeighbor']['file']);own=Path(m['source'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for name,path,box,tile,world in [('upstream-native-x2048',north,[1888,3469,2208,4096],'r05_c03',[10080,19853,10400,20480]),('own-native-x2048',own,[1888,0,2208,627],'r06_c03',[10080,20480,10400,21107])]:
 out=d/(name+'.png');assert not out.exists();Image.open(path).crop(box).save(out);records.append(dict(tile=tile,source=str(path),sourceSha256=sha(path),sourceCropLTRB=box,worldCropLTRB=world,file=str(out),sha256=sha(out),pixels=[320,627],nativePixelScale=1,sourceResampled=False,actuallyViewed=True,viewDetail='original'))
record=dict(status='reopened_due_to_new_native_geometry_evidence',reviewer='/root/resume_r06_c03_fullqa',ownerRootAlsoViewedComposite=True,evidence=records,composite=dict(file=str(d/'edit-target.png'),sha256=sha(d/'edit-target.png'),derivation=str(d/'derivation.json')),finding='Straight vertical splice at tile x2048 (evidence crop x160) displaces gold ornament and turquoise roof grooves. Visible in actual immutable north r05_c03 source and propagated in own r06_c03 first row. Historical corresponding pass is contradicted by these native pixels.',upstreamImagesModified=False,historicalPackagesModified=False,action='Root reopens upstream acceptance; producer does not propagate or modify this north edge. Prepared north material generation not started.',ownPassesReopened=['internal-x2048-segment01.png','north-junction2048.png'],formalAccepted=False)
(d/'reopened-upstream-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=T/'qa/native-repairs-20261013-v02';r=json.loads((q/'review.json').read_text())
for c in r['crops']:
 if Path(c['file']).name in record['ownPassesReopened']:c.update(status='needs_repair',reviewReusedByExactPixelIdentity=False,actuallyViewed=True,notes='New native junction evidence supersedes historical pass: visible vertical x2048 roof splice.',supersedingEvidence=str(d/'reopened-upstream-evidence.json'))
r.update(passed=33,needsRepair=14,newGeometryEvidence=str(d/'reopened-upstream-evidence.json'),formalAccepted=False)
(q/'review-reopened-upstream-20261013.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cp=json.loads((T/'current-fullqa-checkpoint-20261013.json').read_text());cp.update(fullQA=str(q/'review-reopened-upstream-20261013.json'),qaPassed=33,qaNeedsRepair=14,upstreamBoundaryStatus='reopened_actual_r05_c03_x2048_geometry',upstreamEvidence=str(d/'reopened-upstream-evidence.json'));cp['unpassed'].append('actual north r05_c03 and own row1 x2048 geometry splice; north-dependent generation paused')
(T/'current-fullqa-checkpoint-20261013.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
