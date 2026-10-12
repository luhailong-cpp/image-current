import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Restore immutable canonical generation bytes used in composition manifests;
# repair candidates are excluded by their localized role, rejection lives here.
restored=[]
for stem in ['r10_c04_p01_03_v1','r10_c04_stair_upper_v1','r10_c04_stair_lower_v1']:
 p=Z/'native'/f'{stem}.png.generation.json'
 j=json.loads(p.read_text(encoding='utf-8-sig'));j['status']='candidate_pending_seam_qa'
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 restored.append({'path':p.as_posix(),'sha256':sha(p)})
images=[];errors=[];refcount=0
for p in sorted((Z/'native').glob('r10_c04_*.png.generation.json')):
 j=json.loads(p.read_text(encoding='utf-8-sig'));im=Path(j['file'])
 if sha(im)!=j['sha256']:errors.append('image hash '+im.name)
 with Image.open(im) as a:
  a.verify()
 with Image.open(im) as a:
  if a.size!=(1254,1254):errors.append('size '+im.name)
 for r in j['references']:
  refcount+=1
  if sha(r['path'])!=r['sha256']:errors.append('reference hash '+im.name+' '+r['path'])
 for suffix in ['.prompt.txt','.request.json','.receipt.json']:
  if not (Z/'native'/(im.stem+suffix)).is_file():errors.append('missing '+im.stem+suffix)
 images.append({'file':im.as_posix(),'sha256':j['sha256'],'nativeSize':[j['width'],j['height']],'actualModel':j['actualModel'],'actualQuality':j['actualQuality'],'status':j['status'],'record':p.as_posix()})
handoff={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r10_c04','status':'native_coverage_complete_geometry_failed_in_progress','nativeSlotsFilled':16,'successfulGenerationAttempts':len(images),'complete4kCount':0,'formalAcceptedCount':0,'selectedGridVersions':'all 16 v1; p01_03 v2 and p02_03 v2 rejected','preflight':'qa/preflight-r10_c04-v1-candidate-4096.png','knownFailures':[{'issue':'Central staircase column2/3 interface has 40-200px phase/endpoint mismatch; tread meets riser and false short step appears. Not just last stair.','tileCoreRegion':[1750,650,2400,2600],'evidence':['qa/preflight-r10_c04-v1-v2048-part02-100pct.png','qa/preflight-r10_c04-v1-v2048-part03-100pct.png','qa/preflight-r10_c04-v1-intersection-x2048-y2048-100pct.png'],'correctLayout':'Six bright step/landing-edge rhythms in original overview. Last base continuous rising-right line. p03_02 local corner x420..480,y620..690; right exit y240..300; slope about -0.45..-0.50. p03_03 left intercept y350..420, x230 y240..300, top exit x730..850. p02_03 last base enters bottom x240..380 and exits right y760..840; its left intercept is below patch.'},{'issue':'Lower right paving slabs become smaller, inspect whole view after geometry repaired; no claim it passes scale QA.','patches':['p04_03_v1','p04_04_v1']}],'failedRepairs':[{'stem':'r10_c04_p02_03_v2','reason':'Removed stub but did not correct terminal stair slope.'},{'stem':'r10_c04_p01_03_v2','reason':'Native left overlap stair edges changed; pair QA still shows teeth.'},{'stem':'r10_c04_stair_upper_v1','reason':'Whole center straightened but changed outer edges; closed-mask composition moved mismatch to repair boundary.'},{'stem':'r10_c04_stair_lower_v1','reason':'Kept wrong short terminal step and moved mismatches to left repair boundary.'},{'stem':'r10_c04_stair_upper_v2','reason':'Narrow repair still leaves false short steps. Not composed.'}],'repairCompositionEvidence':['qa/repair-r10_c04-upper-v1.manifest.json','qa/repair-r10_c04-upper-v1-trace.json','qa/repair-r10_c04-lower-v1.manifest.json','qa/repair-r10_c04-lower-v1-trace.json'],'compositionMethod':'Sequential four-sided minimum-error hard source mask; no resampling, no feather. Lower source integer crop is from upper composed candidate, not old preflight. Geometry nevertheless failed.','immutableRecordRestoration':restored,'rejectionRecordNote':'stair_upper_v1/stair_lower_v1 canonical generation bytes retained for immutable manifest hashes; localized role prevents prepare reuse. Their failed status is explicit in this handoff, not an approval.','verification':{'pngHashesAndNativeSizesValid':not errors,'checkedImageRecords':len(images),'checkedReferenceHashes':refcount,'errors':errors},'images':images}
p=Z/'qa/r10_c04-worker-handoff.json';p.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'handoff':str(p),'attempts':len(images),'refs':refcount,'errors':errors}))

