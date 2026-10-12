from native_work import *
tid='r03_c13';tile=ZONE/'tiles'/f'{tid}.png';rec=read(tile.with_suffix('.png.derivation.json'))
crops=[]
for r in range(1,5):
 for c in range(1,5):crops.append(f'qa/{tid}-final/core-{r}-{c}-100pct.png')
for i in range(1,4):
 for j in range(1,5):
  crops.extend([f'qa/{tid}-final/vertical-{i}-segment-{j}-100pct.png',f'qa/{tid}-final/horizontal-{i}-segment-{j}-100pct.png'])
for r in range(1,4):
 for c in range(1,4):crops.append(f'qa/{tid}-final/cross-{r}-{c}-100pct.png')
assert len(crops)==49 and all((ZONE/p).exists() for p in crops)
q={'tileId':tid,'file':tile.as_posix(),'sha256':sha(tile),'status':'internal_geometry_not_passed','formalAccepted':False,'reviewedAtUtc':now(),'visualReviewer':'contract_review','recordedBy':'root from completed reviewer message; reviewer interrupted after conclusions delivered and report save delayed','reviewScope':{'coreCrops':16,'seamCrops':24,'crossCrops':9,'allReportedViewed':True,'paths':crops},'findings':[{'severity':'geometry_failure','id':'terrace-front-edge','coreBoundaryX':2048,'approxTileY':[3570,3890],'approxMismatchPixels':[150,220],'evidence':'qa/r03_c13_p04_02_v3__r03_c13_p04_03_v2.join-100pct.png','observation':'Unexplained right-angle vertical face from front edge height mismatch.','nextAction':'After root gate release, redraw complete interrupted edge with all adjoining boundaries.'},{'severity':'layout_risk','id':'vessel-count','observation':'Current adjacent artwork has3round jars+1long-neck vessel; blurred approved overview appears to show3containers. Count not conclusively resolved; flag for design confirmation, do not revoke prior r03_c12 geometry pass solely from blurred guide.'}],'passedObservations':['Lantern native joint overlay continuous','Visible three gourd support feet contact stone plinth plausibly','No other clearly actionable hard geometry break, rectangular seam or material band found in reported whole-tile review'],'externalEdgeReview':'qa/r03_c12__r03_c13-border-review.json','capacity5000Validated':False}
p=ZONE/'qa/r03_c13-whole-review.json'
if not p.exists():write(p,q)
a=ZONE/'tiles/r03_c12.png';b=ZONE/'tiles/r03_c13.png'
q={'pair':['r03_c12','r03_c13'],'sourceHashes':[sha(a),sha(b)],'status':'passed_shared4096edge_visual_only','formalAccepted':False,'reviewedAtUtc':now(),'reviewers':['root','contract_review'],'recordedBy':'root from direct inspection and completed independent reviewer message','edgePixels':4096,'segments':[f'qa/r03_c12__r03_c13.final-border.segment-{i}.png' for i in range(1,5)],'observations':['Gourd silhouette and jade/gold medallion continue','Gourd lower body, support foot and stone plinth continue','Jar and paving surfaces continue'],'limits':'Does not accept all external edges or neighbor internal terrace defect; no gameplay capacity claim'}
p=ZONE/'qa/r03_c12__r03_c13-border-review.json'
if not p.exists():write(p,q)
ack=read(ZONE/'capacity-gate-ack.json')
for rel in ack['auditOutputs']:assert (ZONE/rel).exists(),rel
print(json.dumps({'independentReviewRecorded':True,'ackReferencedAuditFilesAllExist':True,'nativeImages':len(list((ZONE/'native').glob('*.png'))),'pendingNewImageRequests':0,'formalAcceptedCount':0}))

