import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;Q=Z/'qa/r05_c14-v4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=Q/'central-resume-provenance-20261013.json';proof=json.loads(p.read_text())
pending={'p43.png','p44.png','internal-p43-p44.png','repair-cut-bottom.png'}
items=[]
for d in proof['qaPixelProof']+proof['coreQa']:
 d=dict(d);d['visuallyViewedThisTurn']=True;d['verdict']='pending_local_water_tone_repair' if Path(d['path']).name in pending else 'pass';items.append(d)
out={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/central_resume','independentOfGenerator':True,'candidate':proof['candidate'],'status':'independent_review_complete_with_local_water_tone_pending','formalAccepted':False,'internal49':{'viewed':49,'geometryPassed':49,'visualPassed':46,'visualPending':3},'externalWestSouth':{'segmentsPassed':8,'junctionsPassed':7},'repairCutBoundaries':{'viewed':4,'passed':3,'pendingCarriedLocalIssue':1},'coreDetailViewedAtNative1024':16,'quadrantsViewedForContextOnly':4,'provenance':{'path':str(p),'sha256':sha(p),'sourcesVerified':16,'qaPixelProofVerified':56},'items':items,'remainingIssues':[{'id':'r05_c14-water-tone-x3072-y3283','status':'pending_local_visual_repair','geometryPropagationBlocker':False,'candidateApproxBox':[3030,3200,3120,3360],'worldApproxBox':[56278,19584,56368,19744],'description':'Low-contrast vertical water-tone edge at tile-local x3072 below the bridge contribution, visibly ending/crossing a ripple near y3283. Seen at repair-cut-bottom x141,y198 and retained identically in repair-cut-bottom-baseline-v1. The centered bridge removed the stronger original junction L but this short lower continuation remains. Preserve best v4 and repair later; do not treat defer as pass.','affectedQa':['internal-p43-p44.png','central-resume-core-qa/p43.png','central-resume-core-qa/p44.png','repair-cut-bottom.png'],'baselineComparison':{'path':str(Q/'repair-cut-bottom-baseline-v1.png'),'sha256':sha(Q/'repair-cut-bottom-baseline-v1.png')}}],'missingBoundary':'north r04_c14 remains incomplete; east is outer map edge','nextAction':'Continue original c13 column scope using stable r05_c13 north anchors; no c14 source mutation.'}
dest=Q/'central-resume-independent-review-20261013.json';assert not dest.exists();dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(dest),'sha256':sha(dest),'status':out['status']}))
