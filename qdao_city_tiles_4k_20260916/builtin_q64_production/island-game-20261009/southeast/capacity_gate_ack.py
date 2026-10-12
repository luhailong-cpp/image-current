"""Freeze/inventory of existing artwork while shared capacity-layout gate is active."""
from pathlib import Path
from collections import defaultdict
from PIL import Image
import re
from workflow import ROOT,read,write,sha,now
gate=ROOT.parent.parent/'capacity-layout-gate-20261010.json'
assert gate.exists()
gate_data=read(gate)
assert gate_data['holdGenerationAtNewCoordinates']
group=defaultdict(lambda:{'nativeFiles':[],'generatedPatchCoordinates':set(),'repairOutputs':[]})
records=[]
for p in sorted((ROOT/'native').glob('*.png')):
 m=re.match(r'(r\d{2}_c\d{2})(?:_p([1-4][1-4]))?',p.stem)
 if not m:continue
 tid,rc=m.groups();recp=Path(str(p)+'.generation.json')
 im=Image.open(p);d=read(recp) if recp.exists() else {}
 entry={'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'dimensions':list(im.size),'record':recp.relative_to(ROOT).as_posix(),'recordPresent':recp.exists(),'recordHashMatches':d.get('sha256')==sha(p),'status':d.get('status'),'actualModel':d.get('actualModel'),'actualQuality':d.get('actualQuality')}
 group[tid]['nativeFiles'].append(entry);records.append(entry)
 if rc:group[tid]['generatedPatchCoordinates'].add(f'{tid}_p{rc}')
 else:group[tid]['repairOutputs'].append(entry['file'])
tiles=[]
for tid,data in group.items():
 data['generatedPatchCoordinates']=sorted(data['generatedPatchCoordinates'])
 data['uniquePatchCount']=len(data['generatedPatchCoordinates'])
 data['nativeOutputCount']=len(data['nativeFiles'])
 data['tile']=tid;tiles.append(data)
candidates={'r08_c12':'r08_c12.candidate-v3.png','r09_c11':'r09_c11.candidate.png','r09_c12':'r09_c12.candidate-v02.png','r09_c13':'r09_c13.candidate.png','r10_c12':'r10_c12.candidate-v02.png'}
candidate_data=[]
for tid,name in candidates.items():
 p=ROOT/'tiles'/name;assert p.exists()
 candidate_data.append({'tile':tid,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'pixels':list(Image.open(p).size),'formalAccepted':False})
ack={'schemaVersion':1,'zone':'southeast','acknowledgedAtUtc':now(),'gateFile':str(gate),'gateSha256':sha(gate),'status':'holding_new_generation_for_capacity_layout_validation','inFlightStatus':{'root':{'inFlight':False,'lastBatchRecovered':['r11_c12_p32_v01'],'failedWithoutOutput':{'r11_c12_p34_v01':'application network permission was revoked','r11_c12_p41_v01':'401 Unauthorized: missing authentication'},'newCallsAfterGate':0},'tile_left':{'inFlight':False,'currentTile':'r10_c11','generated':['r10_c11_p14_v01'],'p24':'context/prompt only, no call'},'tile_right':{'inFlight':False,'currentTile':'r09_c13','latestSaved':'r09_c13_seam2_v01','r10_c13':'not started'},'coordinate_audit':{'inFlight':False,'currentTile':'r08_c12','latestCandidate':'tiles/r08_c12.candidate-v3.png','latestAttempt':'input read failure, no image output'}},'generatedCoordinates':tiles,'currentCandidates':candidate_data,'counts':{'generatedNativeCount':len(records),'uniqueGeneratedPatchCoordinates':sum(t['uniquePatchCount'] for t in tiles),'fullyCovered4kCount':5,'internalPassed4kCount':3,'externalPassed4kCount':0,'formalAcceptedCount':0},'countDefinitions':{'fullyCovered4kCount':'All4096x4096 pixels covered by generated native sources; does not imply seam/layout acceptance.','internalPassed4kCount':'Current r09c11, r09c12v02 and r10c12v02 have completed internal visual checks; changed regions also checked where revised. r08c12/r09c13 still have flagged internal seams.','externalPassed4kCount':'Number of whole tiles with every required neighbor edge passed, currently0.','formalAcceptedCount':'Final production acceptance, currently0.'},'worldSize':None,'capacity5000Validated':False,'clientMappingValidated':False,'productionNotCancelled':True,'resumeAuthority':'Main orchestrator after layout/scale review; this worker cannot release the gate','allowedWork':['existing pixel QA','provenance replay','mechanical assembly','road and building risk inventory'],'sharedReferenceIssue':'Other workers report approved mail style reference path missing; investigate read-only, never replace historical source hashes.'}
write(ROOT/'capacity-gate-ack.json',ack)
progress=read(ROOT/'progress.json');progress.update(ack['counts']);progress.update(updatedAt=now(),status=ack['status'],currentTile='r11_c12',currentPatch=None,nextStep='Read-only QA and source replay; wait for main orchestrator capacity/layout release',capacityGateAcknowledgment='capacity-gate-ack.json',complete4kCount=5,actualModel=None,actualQuality=None)
write(ROOT/'progress.json',progress)
print({**ack['counts'],'tiles':[{k:t[k] for k in ['tile','uniquePatchCount','nativeOutputCount']} for t in tiles],'recordErrors':[r['file'] for r in records if not r['recordPresent'] or not r['recordHashMatches']]})
