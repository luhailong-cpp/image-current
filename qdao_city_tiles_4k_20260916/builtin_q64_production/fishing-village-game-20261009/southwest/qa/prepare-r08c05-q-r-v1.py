import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent;N=Z/'native'
def ref(p):p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
base=Q/'block2x2-r08r09c05c06-v2-context-native.png';im=Image.open(base);jobs=[]
for rid,box,bounds,intent in [
 ('q_stairedge',[200,920,1454,2174],[220,440,650,820],'ONLY repair the tiny notched stair line near x=400,y=580. The existing broad riser ends at a little jagged break where it touches the next tread. Fill that small break so the same riser bottom edge continues exactly along its present diagonal. Do not move the whole riser or tread. Do not change the position, angle, thickness or texture of any other stair line.'),
 ('r_darkpost',[3340,4260,4594,5514],[210,320,720,900],'ONLY repair the jagged horizontal color cutoff across the dark wooden post near x=420,y=570. Blend the painted wood illumination continuously from the EXISTING warm brown immediately above the cutoff down to the EXISTING very dark brown below. Preserve those top and bottom colors exactly. Keep the straight two post faces, wood grain, exact silhouette and all surrounding red lantern details and paving. Do not brighten the lower post, darken the upper post or recolor the whole post.')]:
 stem='r08_c05_repair_'+rid+'_v1';source=Q/(stem+'-source-1254.png');assert not source.exists();im.crop(box).save(source)
 prompt='Use case: precise-object-edit. Exact native 1254x1254 game map crop. '+intent+' The outer 200 pixels are locked and must remain unchanged. Repair only the small central seam, retaining the original painterly material detail, daylight and Q Daoist style. Return one opaque image exactly 1254x1254, same camera and pixel alignment.'
 pp=N/(stem+'.prompt.txt');pp.write_text(prompt,encoding='utf-8');j={'stem':stem,'tile':'r08_c05','tool':'image_gen__imagegen','route':'builtin','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':{'contextBox':box,'sourceContext':ref(base),'repairBounds':bounds,'margin':40},'submittedParameters':{'transparent_background':False,'referenced_image_paths':[source.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None};save(N/(stem+'.request.json'),j);jobs.append(j)
save(Q/'r08c05-block-repair-jobs-qr-v1.json',jobs)
