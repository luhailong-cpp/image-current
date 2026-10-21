import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
a=Z/'qa/full-tile-r14_c07-assembly.json'
j=json.loads(a.read_text())
defs=[
 ('water-nw',[400,400,1654,1654],[440,420,870,860],'Repair the small angular mismatched water texture patch near image center around x600,y650, creating continuous gently curved turquoise ripple contours. Preserve surrounding ripple positions and scale.'),
 ('rock-west',[350,2530,1604,3784],[180,330,1190,830],'Repair the artificial jagged horizontal tonal/texture cutoff across the rock faces around y540–650. Make each stone face a single coherent hand-painted surface with continuous soft daylight shading and connected natural facets. Preserve rock silhouette, fissures, stone identities, foam and water exactly.'),
 ('rock-east',[1150,2530,2404,3784],[220,330,1130,830],'Repair artificial jagged horizontal tonal/texture cutoff across large rock faces around y540–650. Continue soft gray-blue stone shading naturally from above to below with coherent rounded facets, remove the broad cutoff completely. Preserve stone silhouettes, fissures, foam and water exactly.'),
 ('water-se',[2500,2500,3754,3754],[320,360,910,860],'Repair tiny rectangular tonal mismatch and interrupted ripple/surf contours near image center around x580,y610. Make turquoise ripple contours continuous and organic, with matching fine texture and no rectangular patches. Preserve existing branching foam shapes and all other water.')
]
items=[]
with Image.open(j['output']['path']) as im:
 preview=Z/'qa/r14_c07-composition-preview-v1.png'
 if not preview.exists():im.resize((1400,1400),Image.Resampling.LANCZOS).save(preview)
 for id,box,bounds,fix in defs:
  source=Z/f'qa/r14_c07-{id}-repair-v1-source-native.png'
  assert not source.exists()
  im.crop(box).save(source)
  stem='r14_c07_localrepair_'+id.replace('-','_')+'_v1'
  prompt='Use case: precise-object-edit. This image is a native 1254x1254 crop from a game map. '+fix+' Edit only the described local defect; keep framing, camera, colours, water scale, lighting and all surrounding objects unchanged. Retain clean rounded Daoist Q hand-painted detail, no blur/noise. Output exactly 1254x1254 native pixels, no resize, text, border or new objects.'
  (Z/f'native/{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
  req={'stem':stem,'tile':'r14_c07','patch':id,'coordinates':{'role':'localized native seam repair','globalContextBox':[box[0]+24576,box[1]+53248,box[2]+24576,box[3]+53248],'tileContextBox':box,'expectedNativeDimensions':[1254,1254]},'references':[{'path':source.as_posix(),'sha256':sha(source),'role':'exact native edit target, integer crop from current assembly'}],'submittedParameters':{'model':None,'quality':None,'transparent_background':False}}
  write(Z/f'native/{stem}.request.json',req)
  items.append({'id':id,'stem':stem,'tileContextBox':box,'repairBounds':bounds,'margin':65,'source':{'path':source.as_posix(),'sha256':sha(source)},'prompt':prompt})
write(Z/'qa/r14_c07-localrepair-jobs-v1.json',items)
audit={'schemaVersion':1,'tile':'r14_c07','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'repair_required','candidate':j['output'],'context':j['context'],'assembly':{'path':a.as_posix(),'sha256':sha(a)},'nativeQAViewedCount':39,'nativeQAViewed':j['qa'],'issues':[{k:x[k] for k in ['id','tileContextBox','repairBounds']} for x in items],'formalAccepted':False,'externalJoinsVerified':False}
write(Z/'qa/r14_c07-internal-visual-audit-v1.json',audit)
print(json.dumps(items))
