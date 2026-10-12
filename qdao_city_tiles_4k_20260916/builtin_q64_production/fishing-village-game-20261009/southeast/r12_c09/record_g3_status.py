from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat();sel=rd(R/'selected-patches.json')
sources=[R.parent/'r12_c10/repairs/G3-westjoint-bottom-current-inspection-1254.png',R.parent/'r12_c10/qa/external-continuation-20261011/west-segment-3-100pct.png',R.parent/'r12_c10/qa/external-continuation-20261011/intersection-x36864-y47104-100pct.png']
issue={'id':'G3','status':'confirmed_geometry_repair_required','worldBoundaryY':47219,'affectedCore':'r12_c09:p34','inspectionRegionWorldBox':[36317,47195,36864,47243],'specificVisibleBoardSeamLocationsApproximate':[[36677,47219],[36862,47219]],'description':'At joint adoption bottom y47219, at least two diagonal board-edge grooves show a short step/horizontal termination within c09 p34 core; broader material texture line also follows adoption boundary. Not a color-only issue.','approximationNote':'Exact adoption y; x positions are visually estimated within about10px from unscaled evidence.','evidence':[{'file':str(p),'sha256':sha(p),'native100PercentViewed':True} for p in sources]}
report={'tile':R.name,'reviewer':'south09_resume','createdAt':now,'internalReady':False,'formalAccepted':False,'candidate':sel['candidate'],'candidateSha256':sel['candidateSha256'],'status':'complete_candidate_geometry_repair_required','geometryBlockingFindings':[issue],'priorIndependentPassScope':'Prior weststairs independent pass applies only to its eight named local evidence files and observed riser/rail continuity; it does not close the full outside edge or guarantee unexamined adoption boundary. New G3 evidence supersedes broad tile-ready status.','priorCandidatePreserved':True,'activeSourcePixelsPreserved':True,'railV4Provisional':str(R/'processed/rail-v4-provisional/provisional-selection.json'),'networkRequestsStopped':True}
wr(R/'qa/active-review-20261011.json',report)
snap=R/'selected-before-G3-status-20261011.json'
if not snap.exists():shutil.copy2(R/'selected-patches.json',snap)
sel.update(internalReady=False,formalAccepted=False,status=report['status'],activeReview=str(R/'qa/active-review-20261011.json'),geometryBlockingIssues=['G3'],updatedAt=now)
wr(R/'selected-patches.json',sel)
p=R/'progress.json';pr=rd(p);pr.update(status=report['status'],internalReady4kCount=0,formalAcceptedCount=0,complete4kCandidateCount=1,geometryBlockingIssues=[issue],activeReview=str(R/'qa/active-review-20261011.json'),nextStep='Builtin native repair of G3 only after explicit network restoration; no color camouflage. RailV4 remains provisional awaiting c08 G4/G5 repairs.',updatedAt=now);wr(p,pr)
wr(R/'local-handoff-20261011.json',{'tile':R.name,'activeReview':report,'completeCandidateCount':1,'internalReadyCount':0,'formalAcceptedCount':0,'selectedPatches':16,'provisionalRailSource':rd(R/'processed/rail-v4-provisional/provisional-selection.json'),'gitUntouched':True})
print(json.dumps({'tile':R.name,'internalReady':False,'completeCandidate':1,'blocker':'G3','candidateSha256':sel['candidateSha256']}))
