from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
W=B/'work-r06_c02'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
a=rd(W/'base-v2/r06_c02.candidate.assembly.json')
qa={'updatedAt':now,'tile':'r06_c02','candidate':a['candidate'],'internalAccepted':False,'formalAccepted':False,'coverageCores':16,'nativePixelProof':a['proof'],'reviewStatus':'partial-review-known-failures','reviewed':['all selected native patches and local overlap crops','base-v1 overview and nine 100percent junctions','base-v2 junction-2-3 after repair'],'resolved':['s04_s01 horizontal foliage seam','s04_s03 unexpected lattice window','s03_s04 northwest lintel junction'],'pending':['Roof tile rows mismatch near local x2048, y0..1300; previous two attempts deferred under speed rule','Top ground material junction and row2 roof texture bands remain pending','Full 16core/24seam/external-edge review remains incomplete'],'unchangedChecksReused':True}
wr(W/'base-v2/root-qa.pending.json',qa)
cp={'updatedAt':now,'tile':'r06_c02','selectedCoreCount':16,'candidate':a['candidate'],'assembly':'work-r06_c02/base-v2/r06_c02.candidate.assembly.json','qa':'work-r06_c02/base-v2/root-qa.pending.json','internalAccepted':False,'formalAccepted':False,'builtinImagegenAvailable':True,'actualModel':None,'modelEvidence':'Tool returned no actual model metadata','inFlightGeneration':False,'nextStep':'Resolve remaining roof/ground junctions or advance independent missing cores per two-attempt defer rule; retain pending status.'}
name=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-r06c02-16cores.json'
wr(B/'production-checkpoints'/name,cp)
p=rd(B/'progress.json');p.update(status='native-production-candidate-pending-repair',updatedAt=now,currentTile='r06_c02',currentPatch='16-of-16-core-candidate-base-v2',nextStep=cp['nextStep'],inFlightGeneration=False,currentCheckpoint='production-checkpoints/'+name,lastNewOutput=str(B/'native/r06_c02_s03_s04_v02.png'),fullyCovered4kCount=14,missingFullyCovered4kCount=35,fullyCoveredPendingRepairOrQaCount=2,completeCandidateCoordinatesOnDisk=14)
p['currentCandidates']['r06_c02']={'candidate':'work-r06_c02/base-v2/r06_c02.candidate.png','candidateSha256':a['candidate']['sha256'],'assembly':cp['assembly'],'qa':cp['qa'],'internalAccepted':False,'formalAccepted':False}
p['historicalRuntimeBlocks']=p.pop('runtimeBlocks',[])
p['runtimeStatus']={'rootBuiltinImagegen':'successful','previousGlobalBlockCleared':True,'workerState':'Last resumed agents returned HTTP408; no permission revocation inferred.'}
p['r06c02SelectedNativeCount']=16
wr(B/'progress.json',p)
print(json.dumps(cp))
