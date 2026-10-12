from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from checkpoint_resume import atomic_json
P=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'integrated-20261011/v2/assembly.json'
d=json.loads(P.read_text(encoding='utf-8-sig'))
catalog={'createdAtUtc':d['createdAtUtc'],'status':'merged_4k_candidates_with_open_qa','assembly':{'file':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest()},'tiles':d['outputs'],'preview':d['preview'],'qaReview':str(P.parent/'qa-review.json'),'formalAcceptedCount':0,'remainingIssues':d['remainingIssues'],'nextStep':'Resolve remaining stair/paving-layout and material issues, then renew cross-edge acceptance before generating further southwest tiles.'}
atomic_json(ROOT/'current-candidates.json',catalog)
p=ROOT/'progress.json';progress=json.loads(p.read_text(encoding='utf-8-sig'))
progress.update({'activeTiles':['r10_c05','r10_c06','r11_c05','r11_c06'],'currentCandidateCatalog':str(ROOT/'current-candidates.json'),'latestMergedAssembly':str(P),'latestMergedPreview':d['preview']['file'],'imageGenerationInFlight':False,'inFlightStatus':'reviewing_integrated_candidates','workerStatus':{'productionLines':0,'activeGenerationWorkers':[],'activeGenerationTiles':[],'activeReviewWorkers':['/root/resume_crossedge_audit'],'reportedAtUtc':datetime.now(timezone.utc).isoformat(),'supportActivities':'Native edits completed; reviewing the saved four-tile integrated candidates.'},'nextStepBeforeGate':'修复当前4张候选剩余台阶/铺地布局和材质问题，重新核对相邻边界；随后继续西南其余60张。','selectedNativeSourceCountScope':'Legacy baseline count only; current merged repair contributors are recorded in latestMergedAssembly and its source manifests.','selectedLocalRepairCountScope':'Legacy pre-integration baseline only; not the number of repairs merged on 2026-10-11.','internalPassed4kCountScope':'Current modified candidates require renewed internal review. Historical r10_c05 original approval is retained separately.','historicalInternalPassed4kCount':1,'allCrossEdgesPassed':False})
previous=json.loads(p.read_text(encoding='utf-8-sig'))
for key in ('activeTiles','workerStatus','imageGenerationInFlight','inFlightStatus'):
 if key in previous:progress[key]=previous[key]
progress['nextStepBeforeGate']='完成全部西南64张原生覆盖，修复当前布局及材质问题，逐张及逐边独立验收。'
catalog['nextStep']=progress['nextStepBeforeGate']
atomic_json(ROOT/'current-candidates.json',catalog)
atomic_json(p,progress)
print('Current candidate catalog and progress links saved.')
