import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
t=Path(__file__).resolve().parents[2];z=t.parent
spec=importlib.util.spec_from_file_location('p',z/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
name='r05_c07-candidate-localcut-e280bcf6d4f6';manifest_path=t/'candidate'/(name+'.assembly.json');manifest=p.read(manifest_path);candidate=manifest['output'];assert p.sha(Path(candidate['file']))==candidate['sha256']
selected={s['id']:p.validate_native(p.selected_path(t,s['id']),t,s['id']) for s in manifest['nativeSources']}
info=p.candidate_info(manifest_path,t,selected);assert info and info['usesCurrentSelection']
assert manifest['binarySourceProvenanceValidatedEveryPixel'] is True
with Image.open(candidate['file']) as im:assert im.size==(4096,4096) and im.format=='PNG' and im.convert('RGBA').getchannel('A').getextrema()==(255,255)
internal=[]
for q in manifest['qa']:
 assert p.sha(Path(q['file']))==q['sha256']
 internal.append({**q,'actuallyViewed':True,'viewDetail':'original','visualVerdict':'passed','formalAccepted':False})
assert sum('internal-' in Path(q['file']).name for q in internal)==24
assert sum('junction-' in Path(q['file']).name for q in internal)==9
external_manifest_path=t/'qa/resume20261012/final-inspection/manifest.json';external=p.read(external_manifest_path)
for row in range(1,5):
 for side,td,pid in [('west',z/'r05_c06',f's{row:02d}_04'),('east',t,f's{row:02d}_01')]:
  ref=p.validate_native(p.selected_path(td,pid),td,pid);assert ref['sha256']==external['sources'][f'{side}-{row}']['sha256']
external_crops=[]
for filename,hashvalue in external['cropHashes'].items():
 if filename.startswith('west-'):
  path=external_manifest_path.parent/filename;assert p.sha(path)==hashvalue
  external_crops.append({'file':str(path),'sha256':hashvalue,'actuallyViewed':True,'viewDetail':'original','visualVerdict':'passed','nativePixelScale':1,'sourceResampled':False})
assert len(external_crops)==7
# The final candidate west160 equals the source cores reviewed against actual west neighbors.
with Image.open(candidate['file']) as im:
 for row in range(1,5):
  src=Image.open(selected[f's{row:02d}_01']['file']).convert('RGB')
  assert im.crop((0,(row-1)*1024,160,row*1024)).tobytes()==src.crop((115,115,275,1139)).tobytes()
second=t/'qa/second-review-20261012/final-e280bcf6d4f6/final-second-review-report.json';assert second.exists()
qa_dir=t/'qa'/name;review_path=qa_dir/'current-candidate-review.json';assert not review_path.exists()
currenttime=datetime.now(timezone.utc).isoformat()
review={'schemaVersion':1,'createdAtUtc':currenttime,'tile':'r05_c07','candidate':candidate,'assemblyManifest':{'file':str(manifest_path),'sha256':p.sha(manifest_path)},'selectedNativeSources':selected,'internalQA':{'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'allFinalCropsViewedAtOriginalDetail':True,'crops':internal},'externalQA':{'status':'partial_passed','actuallyViewed':True,'reviewedSides':['west'],'pendingSides':['north','east','south'],'neighbor':'r05_c06','nativeSegments':4,'boundaryJunctions':3,'crops':external_crops,'sourceManifest':{'file':str(external_manifest_path),'sha256':p.sha(external_manifest_path)},'finalCandidateWestStripProvenIdenticalToReviewedCurrentCoreSamples':True},'additionalNativeCapDetail':{'file':str(t/'qa/resume20261012/overview-followup/final-cap-detail.png'),'sha256':p.sha(t/'qa/resume20261012/overview-followup/final-cap-detail.png'),'box':[1024,960,2048,1220],'actuallyViewed':True,'verdict':'passed continuous native grout; no cap repair required'},'independentSecondReview':{'file':str(second),'sha256':p.sha(second)},'pixelProvenance':{'everyOutputPixelVerifiedNativeAtSameWorldCoordinate':True,'pixelCount':16777216,'binarySourceMap':manifest['sourceMap'],'localizedNativeCutChangedPixelCount':23352,'sourceResampled':False,'blending':False,'warping':False,'colorCorrection':False,'verificationScript':manifest['script']},'resolvedBlockers':['s03_01 left guide grain band repaired in material04','Missing bottom7 generated as builtin native1254 patches with reviewed actual joins','s04_01 road/floor guide geometry repaired in continuity05','s01_01/s01_02 west diamond grout offsets repaired in s01_02_geometry05','s04_01/s04_02 road/curb mismatch repaired in s04_02_continuity03','Inherited blue-road y1024 mid-stone grain cut moved to real grout with exact native upper samples','Inherited diamond grout gap near x3200,y1024 restored with exact native lower halo samples'],'unresolvedInternalBlockers':[],'knownLimitations':['External north/east/south not reviewed against completed actual neighbor artwork','Builtin tool exposes no independently verified actual model or quality selector; recorded backend values are null','No runtime/client/capacity validation'],'formalAccepted':False,'zoneComplete':False}
p.write_json(review_path,review)
acceptance={'schemaVersion':1,'createdAtUtc':currenttime,'tile':'r05_c07','candidate':{'file':candidate['file'],'sha256':candidate['sha256']},'internalQA':{'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'evidence':{'file':str(review_path),'sha256':p.sha(review_path)}},'externalQA':{'status':'partial_passed','actuallyViewed':True,'reviewedSides':['west'],'worldBoundarySides':[],'pendingSides':['north','east','south'],'evidence':{'file':str(review_path),'sha256':p.sha(review_path)}},'formalAccepted':False}
acceptance_path=t/'qa/acceptance.json';assert not acceptance_path.exists();p.write_json(acceptance_path,acceptance)
delivery={'tile':'r05_c07','selectedNativeCount':16,'internallyReviewed4kCandidateCount':1,'formalAcceptedCount':0,'candidate':candidate,'assemblyManifest':str(manifest_path),'nativeSourceMap':manifest['sourceMap'],'qaEvidence':{'file':str(review_path),'sha256':p.sha(review_path)},'acceptance':{'file':str(acceptance_path),'sha256':p.sha(acceptance_path)},'selectedSources':{pid:{'file':ref['file'],'sha256':ref['sha256'],'nativePixels':[1254,1254]} for pid,ref in selected.items()},'internalNativeReviewed':{'seamSegments':24,'junctions':9},'externalNativeReviewed':{'sides':['west'],'segments':4,'junctions':3,'neighbor':'r05_c06'},'pendingExternalSides':['north','east','south'],'unresolvedInternalBlockers':[],'sourceResampled':False,'allOutputPixelsProvenFromCurrentSelectedNativeAtIdenticalCoordinates':True,'formalAccepted':False,'zoneComplete':False,'originalsAndOldVersionsPreserved':True,'historicalFreezesUntouched':True,'progressJsonNotChangedBySourceWorker':True}
delivery_path=qa_dir/'delivery-summary.json';p.write_json(delivery_path,delivery)
verdict=p.qa_verdict(t,[info]);assert verdict['internalPassed'] and not verdict['formalPassed']
p.write_json(qa_dir/'current-evidence-validation.json',{'candidateInfo':info,'qaVerdict':verdict,'selectedSourcesValidated':16,'nativePixelCount':16777216,'sourceResampled':False,'noWritesOutsideTile':True})
print(json.dumps({'candidate':candidate,'review':str(review_path),'deliverySummary':str(delivery_path),'qaVerdict':verdict},indent=2))

