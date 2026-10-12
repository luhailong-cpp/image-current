from pathlib import Path
from workflow import ROOT,read,write,sha,now,progress
import json
candidate=ROOT/'tiles/r10_c11.candidate-v03.png'
index=read(ROOT/'qa/r10_c11-final-v03/index.json')
for e in index['items']:
    e.update({'status':'candidate_visual_geometry_pass','reviewer':'tile_left','reviewedAt':now(),'formalAccepted':False})
index.update({'reviewedAt':now(),'all24InternalSeamsGeometryPass':True,'all9JunctionsGeometryPass':True,'formalAccepted':False})
write(ROOT/'qa/r10_c11-final-v03/index.json',index)
for filename in ['r10_c11-junction-repair-v01.json','r10_c11-pillar-repair-v01.json']:
    entries=read(ROOT/'qa'/filename)
    for e in entries:e.update({'status':'candidate_incoming_geometry_reviewed','reviewedAt':now(),'formalAccepted':False})
    write(ROOT/'qa'/filename,entries)
audit=read(ROOT/'qa/r10_c11-source-audit.json')
selected=read(ROOT/'selected-native-r10_c11.json')
used={Path(e['file']).name for e in selected['entries']+selected['overlays']}
unused=[p.name for p in sorted((ROOT/'native').glob('r10_c11*.png')) if p.name not in used]
risks=['Minor paint-scale and tone differences remain around the pillar base near candidate y3470, visible at native resolution; no remaining major contour break found.','The short carved arch groove terminates above the pillar base as generated; design-detail interpretation from blurry layout remains subject to root review.','Left and bottom neighboring tile borders are not yet closed; do not claim external acceptance there.']
report={'tile':'r10_c11','reviewedAt':now(),'candidate':candidate.as_posix(),'sha256':sha(candidate),'dimensions':[4096,4096],'nativeOutputCount':audit['nativeCount'],'baseCoreCount':16,'nativeRepairContributions':2,'allNativeOutputsMeasured1254':True,'all24InternalSeamsGeometryPass':True,'all9JunctionsGeometryPass':True,'repairIncomingEdgesReviewed':8,'northAndEastReviewedSegments':8,'centralFourTileJunctionReviewed':True,'allReviewedExternalPixelsUnchanged':audit['allReviewedExternalPixelsUnchanged'],'base16CoresPixelIdentical':audit['all16BaseCoreContributionsPixelIdentical'],'finalContributionReplayPixelIdentical':audit['finalContributionReplayPixelIdentical'],'sourceAuditErrors':audit['errors'],'historicalMissingReferences':audit['historicalMissingReferences'],'majorGeometryIssues':[],'minorRisks':risks,'unusedVersions':unused,'sourceAudit':'qa/r10_c11-source-audit.json','actualCandidateQA':'qa/r10_c11-final-v03/index.json','externalInheritedReview':'qa/r10_c11-neighborhood-v01/index.json','formalAccepted':False,'status':'complete_4k_candidate_internal_geometry_reviewed_pending_root_material_acceptance','toolErrorHistory':[{'receipt':'receipts/r10_c11_p32_v03-attempt-1-error.json','error':'network error: error sending request','boundedRetrySucceeded':True,'retryResultRejectedForGeometry':True}],'nextStep':'Root review final material consistency and 2x2 candidate preview; do not start new tile before this handoff review.'}
write(ROOT/'qa/r10_c11-quality-review.json',report)
meta=read(Path(str(candidate)+'.generation.json'));meta.update({'status':report['status'],'qualityReview':'qa/r10_c11-quality-review.json','externalEdges':{'top':'all4actualcandidatebands unchanged from root visually reviewed evidence','right':'all4actualcandidatebands unchanged from root visually reviewed evidence','left':'pending neighbor','bottom':'pending neighbor'},'formalAccepted':False});write(Path(str(candidate)+'.generation.json'),meta)
selected.update({'status':report['status'],'qualityReview':'qa/r10_c11-quality-review.json','formalAccepted':False});write(ROOT/'selected-native-r10_c11.json',selected)
progress(status=report['status'],generatedNativeCount=audit['nativeCount'],usableNativeCount=16,repairNativeUsedCount=2,complete4kCount=1,formalAcceptedCount=0,currentPatch=None,candidateFile=candidate.as_posix(),candidateSha256=sha(candidate),qualityReview='qa/r10_c11-quality-review.json',nextStep=report['nextStep'],lastError=None)
print(json.dumps({k:report[k] for k in ['candidate','sha256','nativeOutputCount','all24InternalSeamsGeometryPass','all9JunctionsGeometryPass','finalContributionReplayPixelIdentical','allReviewedExternalPixelsUnchanged','formalAccepted']}))
