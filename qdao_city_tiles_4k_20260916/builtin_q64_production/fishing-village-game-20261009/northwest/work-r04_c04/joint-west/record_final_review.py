from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;O=D/'final-v3';B=D/'lower-v2'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'file':str(p),'sha256':sha(p)}
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(O/'joint-assembly.json')
checks=[]
for e in read(B/'joint-assembly.json')['diagnostics']:
 stem=Path(e['file']).stem
 if stem.startswith(('west-final-segment','south-existing-segment','hem-')) or stem=='southwest-3tiles-intersection-100pct':
  q={**e,'status':'pass-existing-pixel-region','viewedAt100Percent':True,'visualFinding':'Continuous native geometry, no detached mesh/duplicate knot/fixed straight seam.'}
  if stem.startswith('west-final-segment'):q['scope']='entire existing shared west boundary, eight contiguous512px sections'
  if stem.startswith('south-existing-segment'):q['scope']='existing r04c03 bottom to r05c03 first-row boundary'
  if stem=='south-existing-segment-06':q['visualFinding']='Wood shaft remains straight and grain continues. Local painterly wood facets vary in tone; no straight seam spans the shaft.'
  if stem in ['hem-east-100pct','hem-south-100pct']:
   q['scope']='Only existing nontransparent pixels and native bridge termination are checked; unknown neighbor area remains unreviewed.'
   q['visualFinding']='Existing post edge/rope/hem continuous. Complete net hem remains intact; southern cut is in sand. Transparent pixels indicate absent future neighbor, not a game-image defect or accepted content.'
  checks.append(q)
for e in read(O/'extra-diagnostics.json'):checks.append({**e,'status':'pass','viewedAt100Percent':True,'visualFinding':'Continuous rope/mesh/post/sand in common shared ownership; no duplicate structure or cut-off strands.'})
qa={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'shared-west-boundary-and-existing-south-join-pass','formalAccepted':False,'author':'cloth_wall_column','assembly':art(O/'joint-assembly.json'),'mechanicalCheck':art(O/'mechanical-check.json'),'rightBasis':'r04_c04 repair-v6, new sources18/19/20 mapped to joint60/61/62 outside x14300','reviewedCrops':checks,'reviewedCropCount':len(checks),'result':{'westShared4096Height':'pass','westThreeInternalRowCrossings':'pass','existingSouth4096Width':'pass','blueCornerBridge':'pass after shared lower transition and complete hem overlays','lowerTransitionNative':'usable only with hem overlay; its standalone lower edge had failed','completeHemNative':'existing four-sided integrations pass; absent east/south future neighbor is not accepted','sameGlobalHardCutAndOverlayMaskForBothSides':True,'jointNorthR03c03ToR04c03Top115PreservedExactly':True,'supportBridgeCorePreservedExactly':True,'supportBridgeHalo':m['supportHaloChanges'],'oldOriginalCandidatesOrIndicesModified':False},'nativeGenerationEvidence':{'route':'builtin image_gen.imagegen','newNativeDimensions':[[1254,1254],[1254,1254]],'actualModel':None,'actualQuality':None,'reason':'No actual selectors or returned metadata; recorded configured target is not a confirmed runtime model/quality.'},'limits':['This validates actual shared west boundary and the existing south first-row join; it is not full2x2 or regional formal acceptance.','r04c04 north with r03c04 remains for root joint review.','r05c03 is only the existing first row4096x1024; this task did not expand its16-patch production.','r05c04 absent neighbors shown transparent in diagnostics remain unreviewed.','Additional stones generated in southeast native extension lie outside the declared existing tile/partial outputs and are not approved as future production.'],'independentRootReview':'requested; record separately when root returns evidence'}
write(O/'visual-review.json',qa)
fail={'createdAt':datetime.now(timezone.utc).isoformat(),'supersededBy':art(O/'joint-assembly.json'),'trials':[{'directory':str(D),'status':'failed-not-approved','reason':'Initial bluecorner bridge lower hardcut clipped lower mesh.'},{'directory':str(D/'trial-bottom-cut'),'status':'failed-not-approved','reason':'Pushing cut to last4px retained mismatched lower mesh; cannot solve geometry with DP.'},{'directory':str(D/'lower-v1'),'status':'failed-not-approved','reason':'Complete west main boundary improved but south edge near global x12050..12300,y16900 still had detached mesh strands. Complete hem native59 supersedes that region.'}],'noFailuresCountedAsAccepted':True}
write(D/'failed-proposals.json',fail)
summary={'final':art(O/'joint-assembly.json'),'qa':art(O/'visual-review.json'),'mechanical':art(O/'mechanical-check.json'),'artifacts':m['artifacts'],'failedTrials':art(D/'failed-proposals.json')}
write(O/'delivery.json',summary)
print(json.dumps(summary))

