from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
trial=Path(sys.argv[1]); selected=Path(sys.argv[2])
reviews={
'W01':{'geometry':'passed_local','material':'pending_local_shoulder_review','adoptability':'local_improvement_reviewable_not_full_pass','findings':[{'kind':'improved','description':'Spurious diagonal grout branch removed completely; main near-vertical grout and right T-branch retained; no blind stub remains at western fixed edge.'},{'kind':'remaining_material','boxInChildCore':[295,1125,335,1190],'description':'Localized dark shoulder at lower alpha boundary crossing main grout around y1160. Groove remains geometrically connected, but the abrupt shading transition is visible and must not be claimed as full material pass.'}],'observedChangedInternalSeam':'h1024 q0 only; no geometric discontinuity, localized material shoulder recorded'},
'W02':{'geometry':'failed','material':'failed','adoptability':'reject_keep_source_and_trial','findings':[{'kind':'blocking_grout','boxInChildCore':[0,2255,55,2395],'description':'Upper branch still begins blindly at fixed x0 around y2275; incoming west grout around y2360 is not continued. Fixed true-core junction remains disconnected.'},{'kind':'blocking_grout','boxInChildCore':[225,2510,310,2600],'description':'Moved generated lower joint does not meet retained old descending joint at bottom alpha boundary; residual end/shoulder remains.'},{'kind':'material','boxInChildCore':[0,2110,35,2475],'description':'Sharp light/dark slab-face transition along fixed x0 is visible.'}],'protectedLeafTip':'exact original pixels preserved; no leaf clipping introduced by composition'},
'W03':{'geometry':'passed_local','material':'passed_local_patch_only_full_west_W04_unresolved','adoptability':'local_pass_reviewable','findings':[{'kind':'improved','description':'Incoming fixed-core grout at child y3516 extends to main descending grout in a natural junction; lower orphan branch around y3681 removed. Top/right/bottom and protected-paper notch show no new hard cut, double bevel or object clipping.'}],'protectedRedPaper':'exact original pixels preserved'}
}
docs=[]
for sd in sorted(trial.glob('step*')):
 comp=read(sd/'composition.json');job=comp['job'];rv=reviews[job]
 doc={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'assembly_support','method':'Actual native output viewed; all six listed local original-size composition evidence images visually reviewed. No downsample used for conclusion.','sourceComposition':info(sd/'composition.json'),'candidate':comp['core'],'actualNative':comp['actualNative'],'savedAlpha':comp['savedAlpha'],'evidenceReviewed':comp['evidence'],'mechanicalChecks':comp['checks'],'localReview':rv,'formalAccepted':False,'entireWestEdgePassed':False,'published':False}
 dump(sd/'visual-qa.json',doc);docs.append(info(sd/'visual-qa.json'))
idx=read(selected/'trial-index.json')
best=np.array(Image.open(idx['finalTrial']['path']).convert('RGB'))
base=np.array(Image.open(idx['base']['path']).convert('RGB'))
unchanged={}
for orientation in ['v','h']:
 for center in [1024,2048,3072]:
  b=(center-256,0,center+256,4096) if orientation=='v' else (0,center-256,4096,center+256)
  x0,y0,x1,y1=b;unchanged[orientation+str(center)]=bool(np.array_equal(best[y0:y1,x0:x1],base[y0:y1,x0:x1]))
junctions={}
for x in [1024,2048,3072]:
 for y in [1024,2048,3072]:
  junctions[str(x)+'-'+str(y)]=bool(np.array_equal(best[y-450:y+450,x-450:x+450],base[y-450:y+450,x-450:x+450]))
# Each local reviewed image is pixel-identical in the subset trial, despite excluding failed W02.
carried=[]
for sd in sorted(selected.glob('step*')):
 c=read(sd/'composition.json');match=next(p for p in sorted(trial.glob('step*')) if read(p/'composition.json')['job']==c['job'])
 a=read(match/'composition.json')
 assert all(sha(sd/Path(e['path']).name)==e['sha256'] for e in a['evidence'])
 carried.append({'job':c['job'],'composition':info(sd/'composition.json'),'reviewCarriedFrom':info(match/'visual-qa.json'),'allSixLocalEvidenceHashesIdentical':True,'status':reviews[c['job']]})
summary={'schemaVersion':1,'savedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r14_c15','status':'three_actual_native_outputs_saved_and_composed_review_ready_not_published','actualBuiltInSuccessCount':3,'actualModel':None,'actualQuality':None,'networkErrorsThisRound':[],'allThreeTrialIndex':info(trial/'trial-index.json'),'allThreeTrialRejectedForAdoption':'Includes failed W02; retained as reproducible evidence only.','localImprovementCandidateIndex':info(selected/'trial-index.json'),'localImprovementCandidate':idx['finalTrial'],'includedJobs':['W01','W03'],'excludedJobs':['W02'],'localQAReports':docs,'carriedLocalEvidence':carried,'unchangedInternal512Bands':unchanged,'unchangedNine900Junctions':junctions,'internalConclusion':'Previously passed unchanged bands/junctions can be carried forward. Changed h1024 has no geometric break; W01 local material shoulder remains pending.','externalConclusion':{'west':'failed; W02 remains on prior base and W04 full material continuity unresolved; W01 patch shoulder also pending','north':'unchanged from 5ce','east':'unchanged from 5ce','south':'unchanged from 5ce'},'historicalPublished5ceUnchanged':True,'immutableWest728Unchanged':True,'formalAccepted':False,'published':False,'nextAction':'ROOT independent review may adopt selected local improvements without claiming whole-west pass. W02 requires a new narrowly targeted native correction; no repeat performed in this three-request round.'}
dump(D/'production-checkpoint-20261013-W01-W03-review.json',summary)
print(json.dumps({'checkpoint':info(D/'production-checkpoint-20261013-W01-W03-review.json'),'candidate':idx['finalTrial'],'reports':docs,'unchangedInternalBands':unchanged,'nineJunctionsUnchanged':all(junctions.values())}))

