import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent;N=Z/'native'
def ref(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False)
base=Q/'block2x2-r08r09c05c06-v1-context-native.png';im=Image.open(base)
items=[
 ('k_wateredge',[3090,1570,4344,2824],[300,280,970,1200],40,'Repair ONLY the hard right-angle rectangular color boundary in the water near the center-right: make the bright turquoise water transition naturally to the existing darker blue area with continuous painted ripples, preserving exact colors and texture density at the outer border. Remove the straight vertical boundary and horizontal color ledge; keep every lily pad, submerged stone, foliage and masonry exactly in place.'),
 ('l_eastshade',[3500,2180,4754,3434],[320,170,1040,1030],45,'Repair ONLY the abrupt jagged blue-to-dull-green water splice behind the wooden railing. Continue naturally shaded transparent turquoise water with submerged stones from left to right behind the rail, matching the established far-right shadow. Preserve the wooden rails, posts and stone paving pixel positions. Also fix the tiny notches in the stone curb near the middle so each coping slab has one continuous contour. Do not change post scale or add objects.'),
 ('m_westwall',[0,3590,1254,4844],[30,380,1230,950],25,'Repair ONLY the jagged horizontal splice in the retaining-wall base and footpath, running across the middle of this crop: make each pale stone block face continuous and moss joints natural. Remove the thin duplicating sliver or broken wedge at the wall foot. Match the existing stone colors on both sides, preserve all vertical joints and the original wall silhouette. Keep dappled tree shadows and pavement arrangement.'),
 ('n_westpost',[1060,3590,2314,4844],[190,370,890,980],35,'Repair ONLY the strong jagged horizontal color and grain splice crossing the lower third of the tall foreground golden-brown wooden post and its adjacent stone wall. Make the post faces and grain continuous from top to bottom, using gradual natural illumination while matching both unchanged outer border colors. Preserve the exact post silhouette, depth, base and stone joints. Remove the small extra narrow wooden edge strip at the splice, without shifting the post.'),
 ('o_westmasonry',[1720,3590,2974,4844],[90,290,1180,890],30,'Repair ONLY the zigzag horizontal splice across the pale stone retaining wall: connect the same blocks continuously from their upper portions into the lower faces, retaining their exact joints and wall footprint. Remove the sudden tint ledge and projecting triangular pieces along the splice. Preserve the wooden rail, pavement seams, sunlight and moss position. Do not add extra masonry courses.'),
 ('p_centerlamp',[3570,3590,4824,4844],[40,100,1110,980],35,'Repair ONLY two seams: (1) the dark wooden lamp-support post at the left has a sharp jagged horizontal color cutoff near its middle; continue both wood faces and grain smoothly across it using the fixed top and bottom colors. (2) the red-and-gold lantern at center-right has clipped gold rims and a broken cream-panel inner edge at the junction with the right red vertical frame: reconnect each curved gold band and cream panel edge cleanly into that frame. Preserve all lantern positions, dimensions, red frame thickness, silhouettes, neighboring paving and existing lighting. Do not add text or ornaments.')]
jobs=[]
for rid,box,bounds,margin,intent in items:
 stem='r08_c05_repair_'+rid+'_v1';source=Q/(stem+'-source-1254.png');assert not source.exists();im.crop(box).save(source)
 prompt='Use case: precise-object-edit. Image 1 is the exact native map crop to edit. Return one opaque 1254x1254 image at identical scale, camera and coordinates. '+intent+' Keep the outer 120 pixel border aligned to the original, except where the named splice reaches that border. Preserve the established high-definition painted Q Daoist game art, textures and daylight. Do not resize or redesign the scene.'
 pp=N/(stem+'.prompt.txt');pp.write_text(prompt,encoding='utf-8')
 req={'stem':stem,'tile':'r08_c05','tool':'image_gen__imagegen','route':'builtin','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':{'contextBox':box,'sourceContext':ref(base),'repairBounds':bounds,'margin':margin},'submittedParameters':{'transparent_background':False,'referenced_image_paths':[source.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None}
 save(N/(stem+'.request.json'),req);jobs.append(req)
save(Q/'r08c05-block-repair-jobs-v1.json',jobs)
trace=json.loads((Q/'block2x2-r08r09c05c06-v1-trace.json').read_text())
save(Q/'block2x2-r08r09c05c06-v1-visual-audit.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'repairs_required','trace':ref(Q/'block2x2-r08r09c05c06-v1-trace.json'),'qa':[dict(a,viewedAtNativeResolution=True) for a in trace['qa']],'defects':['north-shared part4 water shade cut and curb notches','north-shared part5 and central-junction lantern rim/panel notches','west-shared part1 wall base sliver','west-shared part2 wood post splice','west-shared part3 retaining wall tint/plane splice','west-shared part5 dark lamp support splice'],'inheritedInternalPending':['v4 stair repair minor edge mismatch','e_water right rectangular boundary included as k_wateredge']})
print(json.dumps({'prepared':[j['stem'] for j in jobs]}))
