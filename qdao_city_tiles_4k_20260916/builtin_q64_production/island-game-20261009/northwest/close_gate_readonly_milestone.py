from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
qa=Z/'qa/r03_c03_v5_internal_closure/independent_final_internal_closure_review.json';review=read(qa)
assert review['decision']['internalVisualClosurePassed'] and review['decision']['fourRepairPixelPreservationPassed']
gate=read(Z.parents[1]/'capacity-layout-gate-20261010.json');assert gate['holdGenerationAtNewCoordinates']
proof=dict(path=qa.relative_to(Z).as_posix(),sha256=sha(qa))
metrics=dict(fullyCovered4kCount=1,internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0)
p=read(Z/'progress.json')
p.update(**metrics,status='capacity_layout_gate_active_existing_QA_complete',generatedNativeCount=len(list((Z/'native').glob('*.png'))),generationAttemptCount=len(list((Z/'receipts').glob('*.receipt.json'))),candidateCoordinateCount=30,latest4kCandidate='tiles/r03_c03_candidate-v5_4096.png',complete4kCount=0,legacyComplete4kMeaning='Deprecated completed-deliverable count; retained at0 because external acceptance and reference integrity are unresolved. Use separated counts.',internalPassMeaning='Internal artwork/native seam visual closure and exact four-repair preservation passed for one complete4096 candidate. Does not imply current full reference replay, external edge acceptance, world scale or capacity.',currentFullProvenanceReplayPassed=False,currentFullProvenanceReplayBlock='Missing shared primary style reference at recorded path; no historical sources rewritten.',internalClosureEvidence=proof,candidateCountMeaning='16 base subcell positions of r03_c03 plus four accepted tile-local native repairs form one internally reviewed4096 candidate; other30-coordinate inventory includes partial candidates and rejected attempts.',nextStep='Parent capacity/layout gate release and restoration of required shared style reference are prerequisites to further image generation. Then close r03_c03/r03_c04/r04_c03/r04_c04 contiguous2x2 before remaining49-tile production.',lastError=dict(type='missing_required_style_reference',path='D:/work/image/designs/mail-ui-v1/01-mail-event.png',affects=['future_builtin_reference_input','fresh_full_provenance_replay'],capacityGateAlsoActive=True),updatedAtUtc=now)
write(Z/'progress.json',p)
ack=read(Z/'capacity-gate-ack.json');ack.update(**metrics,readonlyMilestoneComplete=True,updatedAtUtc=now,internalClosureEvidence=proof,currentFullProvenanceReplayPassed=False,workerEvidence=['qa/r03_c04/capacity_gate_ack_20261010.json','qa/r04_c03_firstrow_seams_gate/visual_review_and_road_risks.json','qa/r03_c02_row1/current_review.json'],roadBuildingRiskInventory='qa/capacity_sensitive_artwork_risks.json',newImageGenerationAllowed=False,newCoordinatesAllowed=False)
write(Z/'capacity-gate-ack.json',ack)
s=read(Z/'selected-native.json')
s.update(status='internally_reviewed_first_tile_and_partial_neighbor_candidates_under_capacity_gate',formalAccepted=False,currentCandidate=dict(path=p['latest4kCandidate'],sha256=sha(Z/p['latest4kCandidate']),internalVisualPassed=True,fullCurrentReferenceReplayPassed=False,externalEdgesAccepted=False,review=proof),tileLevelRepairs=[dict(path=f'tiles/r03_c03_candidate-v{n}_4096.native-repair.json',sha256=sha(Z/f'tiles/r03_c03_candidate-v{n}_4096.native-repair.json')) for n in (2,3,4,5)],partialNeighbors=[
 dict(tile='r03_c04',firstRow=['s01_01_a03','s01_02_a01','s01_03_a02','s01_04_a01'],secondRow=['s02_01_a02','s02_02_a02',None,None],status='partial; s02_02 has required wall-skirt repair',evidence='qa/r03_c04/capacity_gate_ack_20261010.json'),
 dict(tile='r04_c03',firstRow=['s01_01_a02','s01_02_a02','s01_03_a03','s01_04_a02'],unacceptedOtherCoordinates=['s02_01_a01','s02_04_a01'],status='first row partial candidate; outer top not accepted; others rejected for propagation',evidence='qa/r04_c03_firstrow_seams_gate/visual_review_and_road_risks.json'),
 dict(tile='r03_c02',selectedLocalCandidate=['s01_04_a02'],unacceptedOtherCoordinates=['s01_03_a01'],status='partial; s01_03 right seam fails',evidence='qa/r03_c02_row1/current_review.json')
],updatedAtUtc=now)
write(Z/'selected-native.json',s)
print(json.dumps(dict(**metrics,generatedNativeCount=p['generatedNativeCount'],generationAttemptCount=p['generationAttemptCount'],gateActive=True,allInflightNone=True)))
