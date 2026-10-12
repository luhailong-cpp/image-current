from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
Q=Z/'qa/r05_c03_v8_internal_closure'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def rec(p): return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p=read(Q/'review_pending.json'); s=read(Q/'connected_agent_standard_review.json'); e=read(Q/'connected_agent_extra_review.json'); n=read(Q/'native_replay.json')
assert s['candidate']['sha256']==p['candidate']['sha256']==e['candidateSha256']==n['base']['sha256']
assert len(s['checks'])==19 and all(x['visualPassed'] and rec(Path(x['path']))['sha256']==x['sha256'] for x in s['checks'])
assert {Path(x['path']).name for x in s['checks']}==set(p['changedStandardCrops'])
assert len(p['unchangedStandardCrops'])==14 and all(x.startswith('PASS:') for x in e['results'].values())
assert n['status']=='base_native_coverage_reverified' and n['proof']['verifiedPixelCount']==4096**2 and n['proof']['priorRepairCount']==7
d={**p,'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'all_33_internal_standard_crops_and_5_extra_repair_boundaries_passed','standardCropCount':33,'changedStandardCropsVisuallyReviewedCount':19,'unchangedStandardCropsPreviouslyReviewedCount':14,'rootAdditionallyReviewedChangedIndices':[0,1,2,3,4,5],'independentStandardReview':rec(Q/'connected_agent_standard_review.json'),'independentRepairBoundaryReview':rec(Q/'connected_agent_extra_review.json'),'priorAll33Review':rec(Z/'qa/r05_c03_v1_root_review.json'),'nativePixelReplay':rec(Q/'native_replay.json'),'nativePixelReplayPassed':True,'candidateRecord':rec(Z/'tiles/r05_c03_candidate-v8_4096.native-repair.json'),'internalVisualAccepted':True,'externalSeamAcceptance':'pending_connected_group_review','formalAccepted':False}
with (Q/'review.json').open('x',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(rec(Q/'review.json')))
