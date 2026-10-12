from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys

b=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    p=Path(p)
    assert p.resolve().is_relative_to(b.resolve())
    temp=p.with_name(p.name+'.finalizing.tmp')
    temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(p)
stamp=datetime.now(timezone.utc).isoformat()
manifest=read(b/'delivery/candidate-manifest.json')
audit=read(b/'qa/provenance-audit/audit-final.json')
assembly=read(b/'qa/region-assembly-verification.json')
net_review=Path(sys.argv[1]).resolve()
assert net_review.is_relative_to(b.resolve()) and net_review.exists()
assert audit['status'] in ('PASS','PASS_PROVENANCE') and audit['errors']==0 and audit['rawCounts']['rawGeneratedImageCount']==71
assert assembly['pass'] and assembly['sha256']==manifest['regionCandidate']['sha256']
assert all(Path(s['file']).exists() for s in manifest['sources'])
refs=[b/'qa/region-seams/findings.json', b/'qa/provenance-audit/audit-final.json',b/'qa/region-assembly-verification.json',net_review,b/'r03_c10/qa/full-audit/findings.json',b/'r03_c10/qa/full-audit/halo-v3/findings.json',b/'r03_c11/qa/qa-review.json',b/'r04_c10/qa/seam-review-v1.json',b/'r04_c10/repairs/north-gold-v1/qa-review.json',b/'r04_c11/qa/right-columns-audit/all-seams/review-v1.json']
assert all(p.exists() for p in refs)
refs.append(b/'qa/region-seams/review-validity-v2.json')
refs.append(b/'qa/root-final-net-review.json')
qa_refs=[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in refs]
manifest.update({'updatedAt':stamp,'productionStatus':'four_tile_candidates_complete','selectedNativeCoreCount':64,'rawGeneratedImageCount':71,'coreNativeVersionCount':66,'additionalBuiltinRepairCount':5,'actualNativeOutputDimensions':[1254,1254],'nativeCoreDimensions':[1024,1024],'withinRegionSeamsReviewed':True,'regionInternalSeamReview':'reviewed_no_blocking_defect_after_recorded_local_repairs','visualReviewMethod':'Full native internal seam review, 17 native region seam crops, and native reinspection of repaired areas. Historical defect reports are retained and superseded by subsequent repair reviews.','qaEvidence':qa_refs,'formalAcceptedCount':0,'externalRegionSeams':'pending_native_neighbors_outside_assigned_region','actualModel':None,'actualQuality':None,'modelQualityEvidence':'Built-in tool does not disclose actual model or quality. Per-image tool receipts are preserved; no inferred model or quality claim.'})
save(b/'delivery/candidate-manifest.json',manifest)
progress=read(b/'progress.json')
progress.update({'updatedAt':stamp,'status':'production_complete_candidates_ready_for_external_seam_review','selectedNativeCoreCount':64,'requiredNativeCoreCount':64,'rawGeneratedImageCount':71,'nextCoordinate':None,'nextAction':'Review assigned region exterior against neighboring native tiles when available.','formalAcceptedCount':0,'withinRegionSeamsReviewed':True,'externalSeamsChecked':False,'deliveryManifest':str(b/'delivery/candidate-manifest.json'),'regionCandidate':manifest['regionCandidate']['file'],'actualModel':None,'actualQuality':None})
for s in manifest['sources']:
    t=s['tile']
    progress['tiles'][t].update({'candidate':s['file'],'candidateSha256':s['sha256'],'dimensions':[4096,4096],'status':'candidate_complete_internal_and_available_neighbor_seams_reviewed','formalAccepted':False,'externalRegionSeamsChecked':False})
    tile_progress={'updatedAt':stamp,'tile':t,'status':progress['tiles'][t]['status'],'selectedNativeCoreCount':16,'requiredNativeCoreCount':16,'nextCoordinate':None,'nextAction':progress['nextAction'],'candidate':s['file'],'candidateSha256':s['sha256'],'qaManifest':str(b/'delivery/candidate-manifest.json'),'formalAccepted':False,'builtinOnly':True,'paidApiUsed':False,'actualModel':None,'actualQuality':None}
    save(b/t/'progress.json',tile_progress)
save(b/'progress.json',progress)
summary={'updatedAt':stamp,'coordinates':manifest['coordinates'],'globalPixelBox':manifest['globalPixelBox'],'status':progress['status'],'tiles':manifest['sources'],'region':manifest['regionCandidate'],'preview':manifest['preview'],'generationCounts':audit['rawCounts'],'nativeMethod':'Each4096 tile uses16 unscaled1024 cores from measured1254 native built-in outputs, with115px halo and recorded local native repairs. The8192 region is an unscaled paste of the four tile candidates.','overviewPixelsUsedInFinal':False,'paidApiUsed':False,'actualModel':None,'actualQuality':None,'formalAcceptedCount':0,'withinRegionSeamsReviewed':True,'exteriorReviewPending':True,'qaEvidence':qa_refs,'manifest':str(b/'delivery/candidate-manifest.json'),'progress':str(b/'progress.json')}
save(b/'delivery/production-summary.json',summary)
print(json.dumps({'status':progress['status'],'tiles':4,'selectedCores':64,'rawGeneratedImages':71,'formalAccepted':0,'manifest':str(b/'delivery/candidate-manifest.json')}))
