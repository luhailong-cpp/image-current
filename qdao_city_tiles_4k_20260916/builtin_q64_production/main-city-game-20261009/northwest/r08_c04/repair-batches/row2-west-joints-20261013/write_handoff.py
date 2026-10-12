from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
provenance=json.loads((B/'combined-provenance.json').read_text())
proposals=[]
for d,p,review in [('joint-x2048-01','lower-adoption-proposal-v2.json','lower-masked-v2-review.json'),('joint-x2048-02','upper-adoption-proposal.json','upper-review.json')]:
 q=json.loads((B/d/p).read_text());r=json.loads((B/d/review).read_text());assert r['status']=='passed_local_native_roi'
 proposals.append({'directory':str(B/d),'proposal':str(B/d/p),'review':str(B/d/review),'source':q['source'],'sha256':q['sourceSha256'],'worldBox':q['sourceWorldBox'],'originInTile':q['sourceOriginInTile'],'roi':q['sameWorldNativeROI'],'tileROI':q['targetTileROI'],'mask':q['mask'],'maskSha256':q['maskSha256'],'pixelCount':q['selectedPixelCount'],'localVisualStatus':'passed','formalAccepted':False})
for p in proposals:assert sha(p['source'])==p['sha256'];assert sha(p['mask'])==p['maskSha256'];assert Image.open(p['source']).size==(1254,1254)
report={'completedAtUtc':datetime.now(timezone.utc).isoformat(),'worker':'/root/r08_c04_row2_local_repair','scope':'r08_c04 row2 x1024 and x2048 local joints only','status':'local_proposals_ready_for_root_integration_and_independent_review','acceptedROIProposals':proposals,'combined':provenance,'combinedSeamCrop':str(B/'x2048-combined-west-seam.png'),'combinedSeamActuallyViewed':True,'combinedSeamFinding':'x2048 grout endpoints connect through native added fitted flagstone and lower corner. Existing non-ROI stone-face material remains original. Does not assert full tile QA.','deferred':[{'tileX':1024,'worldBox':[12685,29581,13939,30835],'originInTile':[397,909],'upperProblemTileBox':[1009,1307,1060,1361],'lowerProblemTileBox':[1009,1699,1060,1755],'attempts':2,'status':'not_passed','evidence':[str(B/'joint-x1024-01/review.json'),str(B/'joint-x1024-02/review.json')],'reason':'Attempt1 moved stone geometry causing ROI perimeter discontinuity; attempt2 creates obvious staircase joint artifacts. No patch from either source adopted.'}],'nativeGeneratedVersionCount':4,'usableNativeSourceCount':2,'selectedCoreCountChange':0,'selectionModified':False,'fullTileModified':False,'gitMutation':False,'resampled':False,'blended':False,'programmaticallyPaintedProductionPixels':False,'modelEntry':'image_gen__imagegen builtin','actualModel':None,'actualModelEvidence':'tool returned no model field; preference 2.5 if existing entry permits, otherwise 2.0 allowed','formalAccepted':False}
(B/'handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print({'handoff':str(B/'handoff.json'),'usableSourceCount':len(proposals),'pixelCount':sum(q['pixelCount'] for q in proposals),'deferredPointCount':2})

