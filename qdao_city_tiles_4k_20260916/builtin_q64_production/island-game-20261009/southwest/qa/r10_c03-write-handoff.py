import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
ROOT=D.parent
prefix='r10c03-rail-v04-r10_c03'
p=D/(prefix+'-candidate-4096.png')
final=np.array(Image.open(p))
scroll=np.array(Image.open(D/'r10c03-scroll-v01-r10_c03-candidate-4096.png'))
local=D/'r10_c03-worker-map.json'
idx=json.loads(local.read_text(encoding='utf-8-sig'))
inputs=json.loads((D/(prefix+'-report.json')).read_text(encoding='utf-8-sig'))['inputs']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
qa={
 'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'tile':'r10_c03','status':'stable native base for root cross-tile and roof-junction integration; not formal acceptance',
 'candidatePrefix':prefix,'candidatePath':p.as_posix(),'candidateSha256':sha(p),'dimensions':[4096,4096],
 'sourceIdMask':(D/(prefix+'-source-id-mask.png')).as_posix(),'report':(D/(prefix+'-report.json')).as_posix(),
 'selectedArray':idx['r10_c03'],'localIndex':local.as_posix(),'nativeSourceCount':18,
 'integrations':[
  {'repair':'r10_c03_pavilion_scroll_join_v01','prefix':'r10c03-scroll-v01','roi':[[0,0,1254,1254]],'band':70,'assessment':'Original rectangular orange seam removed; complete curl geometry continuous. Right trim retains a subtle vertical tonal change; accepted as material variation, no new shape break.'},
  {'repair':'r10_c03_railing_join_v01','prefix':'r10c03-rail-v04','rois':[[0,0,1254,1000],[0,700,1100,1055],[0,850,900,1090],[0,900,800,1140],[0,950,650,1165],[0,950,550,1230],[0,950,350,1254]],'band':15,'mandatoryTarget':[540,210,640,1120],'assessment':'All three horizontal stone members and the lower base are continuous through the former column seam. Reduced stepped union excludes the blue-tile and gold-trim silhouettes. Earlier v01-v03 trials are rejected.'}
 ],
 'nativeVisualReview':{
  'coverage':'All 24 full-length internal seam segments (400x1024 or 1024x400), all nine 600x600 intersections, scroll four perimeter comparisons, railing successive perimeter comparisons and v04 complete target/lower boundary reviewed at native scale. Unchanged areas reviewed on v01; v04 changed railing area separately reviewed fully.',
  'cropInventory':(D/(prefix+'-qa-crops.json')).as_posix(),
  'latestTarget':(D/'r10c03-rail-v04-target-native100.png').as_posix(),
  'latestLowerPerimeter':(D/'r10c03-rail-v04-lower-perimeter-native100.png').as_posix(),
  'preview':(D/(prefix+'-qa-preview-1254-only.png')).as_posix(),
  'acceptedMinorVariations':[
   {'globalBox':[9650,40025,9745,40051],'note':'Small irregular edge at stone-foot contact remains at source perimeter. No new detached object, major silhouette break or blue/gold damage; accepted as minor stone-edge roughness.'},
   {'note':'Small ground facets are more square/gridlike in s02_02; major slab joints remain continuous, recorded material variation.'},
   {'note':'Subtle scroll-right gold tonal edge remains; full curled shape and gold highlight continue.'}
  ],
  'rootPending':[
   {'kind':'roof junction source integration','source':'r10_c03_roof_junction_v01','nativeGlobalBox':[10580,39300,11834,40554],'note':'Existing gold-trim notch near [11100,39810,11160,39855] remains in this base; parent source now ready. Also covers original trim step near [10800,39800,10900,40050].'},
   {'kind':'external cross-tile joins','sources':['r09_r10_c03_package_join_v01','r09_r10_c03_wallfoot_join_v01','r09_r10_c04_steps_join_v01','r10_c03_c04_finial_upper_join_v01'],'note':'Root owns integration and cross-tile review.'}
  ]
 },
 'validation':{'pixelCount':16777216,'mismatchedPixels':0,'sameGlobalCoordinateExact':True,'interpolation':False,'feathering':False,'colorAdjustment':False,'displacement':False,'goldWoodProtectedGlobalBox':[9175,39360,9450,40614],'goldWoodProtectedPixelCount':344850,'goldWoodUnchangedAfterRailing':bool(np.array_equal(final[2496:3750,983:1258],scroll[2496:3750,983:1258]))},
 'sources':inputs,
 'sharedFilesChanged':False
}
assert qa['validation']['goldWoodUnchangedAfterRailing']
out=D/'r10c03-stable-base-handoff.json'
out.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
idx['status']='native_4k_stable_base_handed_to_root'
idx['formalAccepted']=False
idx['candidateArtifacts']={'r10_c03':{'prefix':prefix,'path':p.as_posix(),'sha256':sha(p),'qaHandoff':out.as_posix(),'pendingRootIntegration':True}}
from production import dump
dump(local,idx)
print(json.dumps({'stableBasePrefix':prefix,'candidateSha256':sha(p),'handoff':out.as_posix()}))

