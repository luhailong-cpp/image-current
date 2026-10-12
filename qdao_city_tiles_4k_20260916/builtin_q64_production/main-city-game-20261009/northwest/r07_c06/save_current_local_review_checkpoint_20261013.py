from pathlib import Path
import sys
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
D=T/'qa/current-v07-native-20261013';reg=T/'candidate/native-overlays-20261012-v07.json';m=p.read(reg);entries=[]
findings={
 'r3c4-left':('pending_material_integration','Grout graph is connected in this strip, but the broad main04 ROI still needs stone-grain continuity validation against final c3.'),
 'r3c4-top':('pending_material_integration','No clipped grout tip confirmed in this strip; surface style across the saved r2/r3 boundary needs whole-candidate review.'),
 'r3c4-bottom':('pending_material_integration','Large diamond joints connect; pattern transition between saved r3/r4 sources remains under review.'),
 'r3c4-orphan-roi':('passed_local_scope','Saved05 tiny ROI removes the discarded orphan without erasing the protected gold vertex or introducing locator ink.'),
 'external/west-segment01':('passed_local_scope','Actual complete west-neighbor contours and grout meet across the tile boundary.'),
 'external/west-segment02':('needs_repair','The geometric triangular cap closes, but a rectangular stone-grain cutoff remains near tile (0..160,1139).'),
 'external/west-segment03':('needs_repair','Two grout strokes at the actual west edge around tile y=2590 and y=2700 remain clipped/offset; a shared pinned repair is still needed.'),
 'external/west-segment04':('passed_local_scope','Actual west edge large grout network is continuous; local stone-grain types vary inside complete stone boundaries.'),
 'west-middle-lower-detail':('needs_repair','Exact actual pair crop confirms two clipped west-edge grout tips. Candidate boundaries remain open at the recorded left edge.'),
 'west-row2-cap-detail':('needs_repair','Exact actual pair crop confirms closed triangle but retained rectangular material cutoff above it.')}
for n,(verdict,finding) in findings.items():
 f=D/(n+'.png');entries.append({**ref(f),'name':n,'actuallyViewed':True,'viewDetail':'original','nativePixelScale':1,'verdict':verdict,'finding':finding})
p.write_json(D/'local-checkpoint-review.json',{'createdAtUtc':p.now(),'userLocalDate':'2026-10-13','tile':'r07_c06','candidate':m['candidate'],'registry':ref(reg),'status':'needs_repair_not_deliverable','sourceRecords':27,'pixelProof':m['pixelProof'],'reviewedNativeCrops':10,'entries':entries,'confirmedRemainingDefectGroups':['West row2 cap material cutoff','West row3 lower two grout closures'],'remainingQA':'Full33 internal, all14 actual available north/west crops, and saved r3c4 source perimeter integration are pending; this partial review does not claim full acceptance.','newGenerationSubmitted':False,'newGenerationPausedByExactModelRequirement':True,'modelRequirement':ref(Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')),'rootProjectInstructions':ref(Path('D:/work/image/AGENTS.md')),'formalAccepted':False},replace=False)
p.write_json(T/'current-continuation-checkpoint-20261013.json',{'createdAtUtc':p.now(),'status':'saved_sources_integrated_local_qa_partial_new_generation_paused','tile':'r07_c06','fixedGridNativeCoverage':16,'candidate':m['candidate'],'registry':ref(reg),'localReview':ref(D/'local-checkpoint-review.json'),'alreadyReturnedNativeOutputsPreserved':True,'pendingNativeMain04AndSmall05IncorporatedIntoV07':True,'noNewImagesGeneratedForThisIntegration':True,'fullNativePixelProofPixels':16777216,'fullInternalVisualReviewComplete':False,'internalPassed':False,'formalAccepted':False,'generationHold':ref(Z/'generation-hold-current-model-requirement-20261012.json')},replace=False)
print({'candidate':m['candidate'],'status':'needs_repair','nativeSourceRecords':27})
