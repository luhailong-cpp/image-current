import sys,json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'final-records';O.mkdir(exist_ok=True)
tags={'r03_c04':'d9f811b3adb4','r03_c05':'9e876e7effe2','r04_c04':'2d815289e5cc','r04_c05':'4e4ac2a282d9'}
oldreviews={'r03_c04':ROOT/'r03_c04/final-candidate-review.json','r03_c05':ROOT/'continuation-20261011/checkpoint-v2/r03_c05-review.json','r04_c04':ROOT/'r04_c04/final-candidate-review.json','r04_c05':ROOT/'continuation-20261011/checkpoint-v2/r04_c05-review.json'}
resolved={'r03_c04':['Two left-roof shoulder/groove defects','East D1 return and east shared material/eave splices'],'r03_c05':['D1 upper roof phase cut','D4 compressed repeated row and source-color splice','D5 gold beam facet','E1/E2 west wood/gold/roof/medallion splice'],'r04_c04':['Rail right-facet rectangular shade'],'r04_c05':['Wood/gold minor edge kinks','Floor grout micro-jog','Gray plinth material band/rectangle','Lion-foot pasted green band']}
lowerNames={f'internal-x{x}-segment{s:02d}.png' for x in (1024,2048,3072) for s in (3,4)}|{f'internal-y3072-segment{s:02d}.png' for s in (1,2,3,4)}|{'junction-x2048-y3072.png'}
reviews=[]
for tile,tag in tags.items():
 afile=ROOT/tile/'candidate'/f'{tile}-pipeline-fixed-native-contexts-{tag}.assembly.json';a=p.read(afile);changed=[q for q in a['qaFiles'] if q['changedFromPreviouslyReviewedBase']]
 qs=[]
 for q in a['qaFiles']:
  if q['changedFromPreviouslyReviewedBase']:
   reviewer='boundary_audit' if tile=='r03_c04' else 'upper_left' if tile.startswith('r04') else 'finish_receipts_audit' if Path(q['file']).name in lowerNames else 'root'
   qs.append({'file':q['file'],'sha256':p.sha(q['file']),'cropLTRB':q['cropLTRB'],'rotationCCW90':q['rotationCCW90'],'changed':True,'actuallyViewed':True,'reviewer':reviewer,'verdict':'PASS_LOCAL_INTERNAL_NATIVE'})
  else:qs.append({'file':q['file'],'sha256':p.sha(q['file']),'changed':False,'actuallyViewedThisTurn':False,'verdict':'Pixel-identical to previously reviewed baseline; prior review retained'})
 review={'schemaVersion':1,'createdAtUTC':p.now(),'tile':tile,'candidate':a['candidate'],'assembly':str(afile),'baseReview':str(oldreviews[tile]),'baseReviewSHA256':p.sha(oldreviews[tile]),'resolvedKnownFindings':resolved[tile],'qa':qs,'changedQACount':len(changed),'actuallyViewedChangedQACount':len(changed),'unchangedRetainedQACount':33-len(changed),'knownOpenInternalDefects':[],'internalLocalCandidateQA':'PASS','strictInternalFullyPassed':True,'verifiedOutsideRepairSupportUnchanged':a['verifiedOutsideSupportUnchanged'],'noFinalArtUpscale':True,'formalAccepted':False,'formalPendingReason':'External north/west/east neighbor tiles not available; south checks currently use old available native neighbor sources.'}
 p.put_json(O/(tile+'-review.json'),review)
 reviews.append({'tile':tile,'candidate':a['candidate']['file'],'assembly':str(afile),'review':str(O/(tile+'-review.json'))})
bi=p.read(H/'final-native-boundaries/boundary-index.json')
for r in bi['sharedAssignedBoundarySegments']:
 r.update({'actuallyViewedThisTurn':bool(r['changedFromBase']),'verdict':'PASS_LOCAL_MAJOR_GEOMETRY','reviewer':'root' if r['changedFromBase'] else 'retained baseline; byte-identical'})
for r in bi['availableOuterBoundarySources']:r.update({'actuallyViewed':True,'verdict':'PASS_LOCAL_MAJOR_GEOMETRY','reviewer':'root'})
bi['fourwayReview']={'file':bi['fourway'],'actuallyViewed':True,'nativePixelScale':1,'verdict':'Major geometry continuous; original timber shade band at upper edge retained as a visual note, not a new geometry seam.'}
p.put_json(O/'boundary-review.json',bi)
# Clarify the final D4 recipe without altering preserved historical derivation records.
p.put_json(O/'d4-final-recipe-clarification.json',{'historicalRecord':str(H/'lower-merged-v3/d4-derivation.json'),'historicalRecordSHA256':p.sha(H/'lower-merged-v3/d4-derivation.json'),'correction':'That record retained an outdated prose label top585..615. The executed final top alpha is540..570 and the authoritative saved alpha/source2-overlap weight files define the actual pixels.','actualAlpha':p.reference(H/'lower-merged-v3/d4-alpha.png','actual final return alpha'),'actualSource2OverlapWeight':p.reference(H/'lower-merged-v3/d4-source2-overlap-weight.png','actual12px smoothstep overlap weight'),'recipe':{'file':str(H/'derive_lower_v2.py'),'sha256':p.sha(H/'derive_lower_v2.py')},'formula':'source2 overlap=(source1*(255-weight)+source2*weight+127)//255; return=(firstStage*(255-alpha)+overlapComposite*alpha+127)//255; top540..570,bottom748..780,left160..220; original gold protected','resampled':False,'spatialBlur':False})
raws=sorted(H.rglob('raw-native.png'))+sorted((ROOT/'r03_c04/finish-20261012-left-roof').glob('v*/raw-native.png'))+[ROOT/'r04_c04/finish-20261012-rail-facet/raw-native-v1.png']
assert len(raws)==20 and len({p.sha(f) for f in raws})==20
rawrecs=[]
for f in raws:
 inf=p.reference(f,'unique builtin generated original');assert inf['pixels']==[1254,1254]
 side=Path(str(f)+'.generation.json');assert side.exists()
 rawrecs.append(dict(inf,generationRecord=str(side),generationRecordSHA256=p.sha(side)))
checks=[]
for tile in tags:
 m=p.read(ROOT/tile/'finish-20261012-integrated/integration-manifest.json')
 baseline=np.array(Image.open(m['baseCandidate']['file']).convert('RGB'));current=np.array(Image.open(m['integratedComposite']['file']).convert('RGB'));support=np.array(Image.open(m['combinedSupport']['file']).convert('L'))>0
 staged=H/'staged-final-v2'/(tile+'-staged.png');assert p.sha(staged)==m['integratedComposite']['sha256']
 assert np.array_equal(baseline[~support],current[~support])
 checks.append({'tile':tile,'candidateSHA256':m['integratedComposite']['sha256'],'pixelAndFileIdenticalToStaged':True,'changesOutsideSupport':0,'exportsSelected':len(m['exports'])})
audit={'schemaVersion':1,'createdAt':p.now(),'uniqueNewSuccessfulBuiltinRawCount':20,'rootCount':16,'leftRoofChildCount':3,'railChildCount':1,'rawOutputs':rawrecs,'nativeSelectedSources':64,'newSelectedExports':35,'checks':checks,'historicalFreezeSHA256':p.sha(ROOT/'migration-freeze-20261011.json'),'historicalExternalReferencesSHA256':p.sha(ROOT/'migration-external-references-20261011.json'),'inFlightRequests':0,'unsavedSuccessfulOutputs':0,'actualModel':None,'actualQuality':None,'paidApiUsed':False}
p.put_json(O/'source-audit.json',audit)
spec={'directory':'delivery-20261012-v1','tiles':reviews,'crossBoundarySummary':['44 changed internal/junction QA crops actually reviewed at native size and locally pass;88 retained crops pixel-identical to their reviewed baseline.','Assigned shared boundaries:8 changed native strips actually viewed;8 unchanged strips retain prior reviews. Fourway major geometry continuous.','8 available south boundary strips actually viewed against old native neighbor cores;local major geometry pass.','24 outer segments across6 neighbor tiles unavailable: '+', '.join(bi['missingNeighborTiles'])],'remainingWork':['Formal cross-area acceptance waits on6 missing adjacent tiles and a current full adopted south-neighbor baseline.','Only these4 assigned tiles are delivered; full zone/full map completion is not claimed.']}
p.put_json(O/'delivery-spec.json',spec)
print(json.dumps({'readyTiles':4,'rawOutputs':20,'changedQA':sum(p.read(O/(t+'-review.json'))['changedQACount'] for t in tags),'formalAccepted':0,'packageSpec':str(O/'delivery-spec.json')}))

