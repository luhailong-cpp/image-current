import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from datetime import datetime,timezone
z=Path(__file__).resolve().parents[1];q=z/'qa';pre='repair-r08_c06-internal-v5'
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
idx=rd(q/(pre+'-qa-index.json'));records=[]
previous5=['v1024-part05','v2048-part01','v2048-part02','v2048-part03','v2048-part04']
for r in idx['original39']:
 if r['unchangedPixels']:records.append({'file':r['original']['file'],'status':'pass_inherited_exact_original_pixels'})
 else:
  p=Path(r['updated']['path']); prior=None
  for short in previous5:
   if p.name==pre+'-'+short+'-100pct.png':
    old=q/('repair-r08_c06-internal-v4-'+short+'-100pct.png')
    assert np.array_equal(np.array(Image.open(p)),np.array(Image.open(old)));prior=ref(old)
  records.append({'file':ref(p),'status':'pass','inspectionScale':'original_100pct','exactSameAsViewed':prior})
final=[]
for r in idx['finalcrops']:
 p=Path(r['path']);prior=None
 if r['id'] in ['h_upperpaving','b_rightsign','e_frontcanopy']:
  old=q/('repair-r08_c06-internal-v3-'+r['id']+'-finalcrop-100pct.png')
  assert np.array_equal(np.array(Image.open(p)),np.array(Image.open(old)));prior=ref(old)
 final.append({'id':r['id'],'file':ref(p),'status':'pass','inspectionScale':'original_100pct','exactSameAsViewed':prior})
t=rd(q/(pre+'-trace.json'))
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c06','status':'internal_visual_qa_passed_south_join_pending','trace':ref(q/(pre+'-trace.json')),'context':t['context'],'candidate':t['candidate'],'qaIndex':ref(q/(pre+'-qa-index.json')),'original39':records,'repairFinalCrops':final,'summary':{'baseQa39':39,'unchangedInherited':11,'updatedInspected':28,'repairCropCount':8,'resolved':['H stone paving sharpness and boundary continuity','A one coherent lantern and tassel','B right red sign band and old small red triangle removed','C/D broad blue cloth collage band removed','E front canopy outline notch and mask-edge kink removed','F golden rim offset with whole native crop selected after narrow masks failed','G wood surface grain and shadows continuous'],'remainingInternalBlockers':[]},'pixelMethod':{'nativePixelsResampled':False,'feathered':False,'colourCorrected':False,'allFinalPixelsExactlyMatchRecordedSources':t['validation']['allFinalPixelsExactlyMatchRecordedSource']},'notClaims':['runtime game validation','walkability capacity validation','formal global acceptance'],'supersedesWorkingCandidateOnly':ref(q/'repair-r08_c06-internal-v2-trace.json'),'historicalFreezeAndAuditUnmodified':True}
out=q/(pre+'-internal-qa.json')
with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
south=q/'block2x2-r09r10c05c06-v1-r09_c06-context-native.png'
assert ref(south)['sha256']=='7cda883269fefa3b54c32a6c6720b97fe3c04710ba94a98b632aef9253839e55'
m={'outputPrefix':'pair-r08c06-r09c06-v1','inputs':[{'tile':'r08_c06','context':t['context']},{'tile':'r09_c06','context':ref(south)}],'provenance':[ref(q/(pre+'-trace.json')),ref(out),ref(q/'block2x2-r09r10c05c06-v1-trace.json')]}
with (q/'pair-r08c06-r09c06-v1.manifest.json').open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)
print(json.dumps({'report':ref(out),'manifest':ref(q/'pair-r08c06-r09c06-v1.manifest.json')}))

