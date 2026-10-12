from pathlib import Path
from PIL import Image
import json,hashlib,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
obj=sys.argv[1]
if obj=='floor':
 name='r12_c13_floor_end_joint_whole_v01';origin=[397,1421]
 desc='''Repair only the incomplete plank boundaries near the middle vertical guide join x627, around y150..1050. Preserve all board long edges reaching the crop exterior. In the upper set of long floor boards the two sides have slightly different board widths. In the lower set one black gap has a free end on flat wood around x627,y745. Resolve those width differences with complete short diagonal board-end joints that traverse the FULL width of the affected plank. Each short end joint must connect both neighboring long black plank gaps, with physical T junctions at both ends. The left and right long gap segments are staggered in height: use one complete end joint spanning both heights and ending on the next long gap; do not connect them with only a tiny vertical notch. No floating endpoint, fading scratch, extra long parallel groove, blind T, or thin seam stopping in wood. Keep the golden wood, grain and exact outer endpoints. Keep the existing rail at the extreme upper right fixed. Do not redecorate or create props.'''
elif obj=='sail':
 name='r12_c13_lower_sail_batten_whole_v01';origin=[2445,2842]
 desc='''Repair only the lowest orange wooden sail batten, around y700..1050. The artificial guide cut x627 makes this single straight batten jump vertically by about 50 pixels. Restore the entire visible straight batten between its fixed left and right outer endpoints into one physically continuous golden top face and dark brown underside, with one uninterrupted straight upper contour and lower contour and a consistent shadow on the cloth. No step, offset splice, extra joint, double beam, vertical boundary, or narrowing at x627. Preserve the upper batten, all sail stitching, mast/support on far left, pale ivory cloth and existing outer crop geometry. The cloth weave and lighting across x627 must also be continuous. Correct the whole lower beam and its cloth shadow, keeping other objects fixed.'''
else:raise ValueError(obj)
src=R/'tiles/r12_c13.candidate-sol-20261012-v02.png';im=Image.open(src).convert('RGB');g=R/'guides'/f'{name}.native-edit.png';assert not g.exists();box=[origin[0],origin[1],origin[0]+1254,origin[1]+1254];im.crop(tuple(box)).save(g)
coord={'id':name.rsplit('_',1)[0],'tile':'r12_c13','tileRelativeOrigin':origin,'nativeGlobalBox':[49152+origin[0],45056+origin[1],49152+origin[0]+1254,45056+origin[1]+1254],'coreGlobalBox':[49152+origin[0]+115,45056+origin[1]+115,49152+origin[0]+1139,45056+origin[1]+1139],'nativePixels':[1254,1254],'coreCrop':[115,115,1139,1139]}
write(Path(str(g)+'.generation.json'),{'file':g.as_posix(),'sha256':sha(g),'operation':'exact unscaled candidate-source crop; edit guide only','usableAsFinalArt':False,'derivedFrom':[{'file':src.as_posix(),'sha256':sha(src)}],'sourceCrop':box,'coordinate':coord})
refs=[{'file':g.as_posix(),'sha256':sha(g),'role':'precise edit target registered complete physical-object crop'}]+read(R/'references.json')
prompt='Use case: precise-object-edit. Edit image 1 as the complete same 1254-square native daylight painted map crop. Keep the exact crop, camera, scale and material/style of the original. The outer 115-pixel border is fixed geometry. Last three images specify layout, material and painting style only.\n'+desc+'\nOne opaque square at existing scale, no panels, text, UI, people or new objects.'
pp=R/'prompts'/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8');rp=R/'prompts'/f'{name}.request.json';assert not rp.exists();write(rp,{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'coordinate':coord,'submittedParameters':{'model':None,'quality':None},'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'resumeAuthorization':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','dispatchStatus':'prepared_not_submitted'})
print(json.dumps({'name':name,'guide':g.as_posix(),'origin':origin,'coreDestination':[origin[0]+115,origin[1]+115,origin[0]+1139,origin[1]+1139]}))
