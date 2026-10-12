from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r03_c10')
Q=R/'qa'/'full-audit'/'halo-v3';P=R/'candidate'/'r03_c10-4096-candidate-v3.manifest.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(R/'candidate'/'r03_c10-4096-candidate-v1.png')=='1bffe80cb6357c27f4ed06b66f517c1d85e8410844c2bd6f9215aefb64d5cfb6'
assert sha(R/'candidate'/'r03_c10-4096-candidate-v2.png')=='39be3ec5b0dbb3438c978a0d36c9a13c2f63d67e5d6ebefcf3f7c68e68bbc0cc'
m=json.loads((Q/'metrics.json').read_text())
result={'tile':'r03_c10','candidate':str(R/'candidate'/'r03_c10-4096-candidate-v3.png'),'sha256':sha(R/'candidate'/'r03_c10-4096-candidate-v3.png'),'status':'native halo stitch passed targeted internal seam review','formalAccepted':False,'externalSeamsChecked':False,
'visualInspection':{'scale':'original native pixels; no display-derived conclusions from preview alone','evidence':['v3-left-transition-native.png','v3-center-native.png','v3-right-middle-native.png','v3-right-native.png','v3-right-edge-transition-native.png','v3-vertical-seam-native.png'],'findings':'No double ribs, broken rim, new hard band, or new abrupt transition observed. Horizontal paper-tone step is resolved across the blended canopy. Existing vertical correction remains smooth. Native leaves and rear timber remain coherent through the 32px side transitions. Whole-tile preview shows no broad rectangular tone patch.','geometricGhostingObserved':False,'rejected':False},
'quantitativeExamples':[{'seam':'y1024','xRangeHalfOpen':[2286,2675],'v2MeanAbsoluteRGBJump':9.739502906799316,'v3MeanAbsoluteRGBJump':1.7189373970031738,'v3NearbyTextureMean':1.6863200664520264,'reductionPercent':100*(1-1.7189373970031738/9.739502906799316)},{'seam':'y1024','xRangeHalfOpen':[2675,3072],'v2MeanAbsoluteRGBJump':10.099916458129883,'v3MeanAbsoluteRGBJump':1.248530626296997,'v3NearbyTextureMean':1.1592860221862793,'reductionPercent':100*(1-1.248530626296997/10.099916458129883)},{'seam':'x2048 y384..1024','v2MeanAbsoluteRGBJump':1.2416666746139526,'v3MeanAbsoluteRGBJump':1.2416666746139526,'result':'unchanged, previous vertical repair preserved'}],
'invariants':{'measuredNativeSources':[1254,1254],'trueOverlapHeight':230,'overlapTileYHalfOpen':[909,1139],'nativeScale':1,'resampling':False,'paintingOrColorFiltering':False,'v1AndV2ShaUnchanged':True,'nativeSourcesUnchanged':True,'outer115PixelStripsByteIdentical':True,'allPixelsOutsideHorizontalOverlapByteIdenticalToV2':True,'changedBoundingBoxComparedToV2':m['v3ChangesRelativeToV2Box']},
'provenance':'Full source selection/generation-record hashes, all local/full alpha masks, full float weights, exact reproducible script and previous candidate hashes are in the v3 manifest.',
'remainingWork':[{'issue':'Pre-existing bottom gold-tip blur in p41','owner':'root','status':'left unchanged for builtin localized correction'},{'issue':'External tile seams','status':'not reviewed here'}],
'supersedes':'The horizontal-tone residual documented in tint-v2/findings.json is resolved by this native-halo stitch. This report does not grant formal whole-tile acceptance.',
'reviewedAt':datetime.now(timezone.utc).isoformat()}
(Q/'findings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads(P.read_text())
manifest.update({'status':'native_halo_stitch_passed_targeted_internal_seam_review','formalAccepted':False,'externalSeamsChecked':False,'geometricGhostingObserved':False,'primaryRepairsPassed':True,'review':{'file':str(Q/'findings.json'),'sha256':sha(Q/'findings.json')}})
P.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':result['candidate'],'sha256':result['sha256'],'report':str(Q/'findings.json'),'status':result['status']}))

