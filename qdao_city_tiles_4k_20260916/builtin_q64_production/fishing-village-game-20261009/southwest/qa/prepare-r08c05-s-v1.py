import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
Q=Path(__file__).resolve().parent;N=Q.parent/'native'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
base=Q/'block2x2-r08r09c05c06-v3-context-native.png';box=[4310,3750,5564,5004];stem='r08_c05_repair_s_pavejoint_v1';source=Q/(stem+'-source-1254.png');assert not source.exists();Image.open(base).crop(box).save(source)
prompt='Use case: precise-object-edit. Exact native 1254x1254 game map crop. Repair ONLY the tiny doubled zigzag offset in the pale diagonal paving joint near x=280,y=400, where two flat stone tiles accidentally form overlapping broken corners. Remove that tiny overlaid sliver, and join the existing long diagonal tile edge smoothly through this point. Preserve the surrounding original paving geometry, stone color and texture, all other joints and original daylight. The red lantern at left and wooden blue-covered table at right are locked completely unchanged. All outer 200 pixels locked unchanged. No zoom, no reframing, no added objects, no global texture or color changes. One opaque native 1254x1254 image, exact original alignment and painted material style.'
pp=N/(stem+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
j={'stem':stem,'tile':'r08_c05','tool':'image_gen__imagegen','route':'builtin','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':{'contextBox':box,'sourceContext':ref(base),'repairBounds':[170,310,520,560],'margin':30},'submittedParameters':{'transparent_background':False,'referenced_image_paths':[source.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None}
for p,a in [(N/(stem+'.request.json'),j),(Q/'r08c05-block-repair-jobs-s-v1.json',[j])]:
 with p.open('x',encoding='utf-8') as f:json.dump(a,f,indent=2)
