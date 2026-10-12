from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
B=Path(__file__).resolve().parent;O=B/'work-r05_c02/base-v1'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cp=O/'r05_c02.candidate.png';ap=O/'r05_c02.candidate.assembly.json';a=rd(ap);assert a['proof']['mismatches']==0 and a['proof']['pixels']==16777216 and a['candidate']['sha256']==sha(cp)
q={'tile':'r05_c02','candidate':{'file':str(cp),'sha256':sha(cp)},'assembly':{'file':str(ap),'sha256':sha(ap)},'internalAccepted':True,'status':'internal-native-seams-pass-external-pending','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','coverage':{'cores':16,'verticalSeams':12,'horizontalSeams':12,'junctions':9,'externalNorthSegments':4,'externalEastSegments':4},'visualEvidence':{'contactManifest':str(O/'qa-contacts/manifest.json'),'contactManifestSha256':sha(O/'qa-contacts/manifest.json'),'display':'Viewed all13 contacts with original image detail, no resampling; first two default-detail views repeated at original detail.'},'notes':['Red and blue net strands, knots and supports continuous. Wooden pole, rope wraps and stone base continuous across core joins.','Lower-left canopy and small brown roof corner follow layout; curved ridge, finial and tile rows continuous.','Minor painterly ground texture variation remains gradual within sparse pebbles; no geometry break or abrupt seam requiring repair found.'],'nativeProof':a['proof'],'boundaries':{'north':'pass with adopted r04_c02','east':'pass with adopted r05_c03','south':'neighbor production pending','west':'neighbor production pending'},'formalAccepted':False,'missingOuterNeighborsAreNotMissingLocalNative':True}
qp=O/'root-qa.json';wr(qp,q)
ip=B/'current-artifacts.json';idx=rd(ip);snapshot=O/'current-artifacts.before-adoption.json'
if not snapshot.exists():wr(snapshot,idx)
idx['r05_c02']={'candidate':cp.relative_to(B).as_posix(),'assembly':ap.relative_to(B).as_posix(),'qa':qp.relative_to(B).as_posix(),'status':'internally-accepted-north-east-boundaries-passed-candidate','formalAccepted':False}
tmp=ip.with_suffix('.tmp.json');wr(tmp,idx);os.replace(tmp,ip)
r=rd(B/'production-resume-20261012.json');r.update(currentTile='r05_c02',currentPatch='complete-internal-QA',inFlightGeneration=False,selectedCurrentTilePatches=16);r.setdefault('completedThisResume',[]).append('r05_c02 full native candidate and root QA adoption');wr(B/'production-resume-20261012.json',r)
p=rd(B/'progress.json');p.update(currentPatch='complete-internal-QA',inFlightGeneration=False,r05c02SelectedNativeCount=16);wr(B/'progress.json',p)
print(json.dumps({'adopted':'r05_c02','sha256':sha(cp),'qa':str(qp)}))
