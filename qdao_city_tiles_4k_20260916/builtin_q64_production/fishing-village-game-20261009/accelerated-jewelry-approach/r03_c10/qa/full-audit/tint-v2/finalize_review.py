from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r03_c10')
Q=R/'qa'/'full-audit'/'tint-v2'
P=R/'candidate'/'r03_c10-4096-candidate-v2.manifest.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((Q/'metrics.json').read_text())
assert sha(R/'candidate'/'r03_c10-4096-candidate-v1.png')=='1bffe80cb6357c27f4ed06b66f517c1d85e8410844c2bd6f9215aefb64d5cfb6'
report={
'tile':'r03_c10','candidate':str(R/'candidate'/'r03_c10-4096-candidate-v2.png'),
'candidateSha256':sha(R/'candidate'/'r03_c10-4096-candidate-v2.png'),
'status':'targeted native repair candidate completed; residual internal tone seam requires review',
'formalAccepted':False,'externalSeamsChecked':False,
'visualInspection':'Target and builtin result inspected at native 1254x1254. Composite and all four feather transitions inspected through unscaled 512x1088 and 603x1043 crops, plus rib/rim and horizontal-seam crops. Whole tile preview inspected.',
'primaryVerticalRepair':{'result':'Pass for targeted seam: straight vertical tint step removed; no doubled ribs or broken bamboo/rim geometry observed. Feather boundaries do not introduce a new rectangular border.','meanAdjacentRGBJumpBefore':m['before']['meanAbsoluteAdjacentRGBJump'],'meanAdjacentRGBJumpAfter':m['after']['meanAbsoluteAdjacentRGBJump'],'reductionPercent':m['meanJumpReductionPercent'],'nearbyTextureJumpAfter':m['after']['neighbor32ColumnMeanAbsoluteRGBJump']},
'invariants':{'measuredRepairNativeDimensions':[1254,1254],'candidateDimensions':[4096,4096],'nativePixelsResized':False,'allFourOuter115PixelStripsByteIdentical':True,'allPixelsOutsideRoiByteIdentical':True,'v1SourceShaUnchanged':True,'nativesAndSelectionsModified':False,'roiTileXYXYHalfOpen':[1811,358,2286,1273],'actualChangedBoundingBoxTileXYXY':m['changedPixelBoundingBoxTileXYXY']},
'remainingFindings':[{
'priority':2,
'kind':'pre-existing horizontal paper-tone step',
'seam':'tile y1024, p12-p22 / p13-p23 / p14-p24',
'description':'Wider native context reveals a horizontal yellow paper-tone step, most visible outside the narrow repaired strip. The same discontinuity is present in v1; native compositing reduces it in the middle but does not alter it outside the authorized ROI. No geometric break is observed.',
'confirmedExampleFaultBoxTileXYXY':[2286,1008,3072,1040],
'confirmedExampleFaultBoxGlobalXYXY':[39150,9200,39936,9232],
'nextReviewContextBoxesTileXYXY':[[1421,768,2675,1280],[2675,768,3929,1280]],
'metricsFile':str(Q/'horizontal-residual-metrics.json'),
'exampleBeforeAfterUnchangedJump':{'xRangeHalfOpen':[2286,2675],'yBoundary':1024,'meanAbsRGBJump':9.739502906799316,'neighborMeanAbsRGBJump':1.9669679403305054},
'action':'Retain v2 as successful vertical-seam repair. Review/repair the remaining horizontal parasol-tone line with native builtin generation before declaring all internal seams cleared. Preserve existing ribs/rim; do not stretch or move pixels.',
'evidence':['before-roi-transition-native-603x1043.png','after-roi-transition-native-603x1043.png','remaining-horizontal-tint-native.png','remaining-horizontal-right-native.png']
}],
'correctionToPriorAudit':'The first audit understated horizontal-y1024 color continuity. Expanded native context during repair verification revealed the existing horizontal line; this report supersedes the earlier no-defect color assessment for that seam. Earlier geometry-continuity findings stand.',
'provenanceManifest':str(P),'reviewedAt':datetime.now(timezone.utc).isoformat()
}
(Q/'findings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads(P.read_text())
manifest.update({'status':'targeted_native_repair_candidate_completed_internal_residual_tint_review_required','formalAccepted':False,'externalSeamsChecked':False,'visualReview':{'file':str(Q/'findings.json'),'sha256':sha(Q/'findings.json')},'primaryRepairPassed':True,'remainingInternalFindings':1})
P.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':report['candidate'],'candidateSha256':report['candidateSha256'],'report':str(Q/'findings.json'),'primaryRepairPassed':True,'remainingInternalFindings':1}))

