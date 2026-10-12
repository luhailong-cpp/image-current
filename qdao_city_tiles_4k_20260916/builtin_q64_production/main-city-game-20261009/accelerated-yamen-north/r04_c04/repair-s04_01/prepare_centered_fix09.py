from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix09_centered';D.mkdir(parents=True,exist_ok=True)
north=B/'fix08/generated.png';south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
N=Image.open(north).convert('RGB');S=Image.open(south).convert('RGB')
target=Image.new('RGB',(1254,1254));target.paste(N.crop((0,512,1254,1139)),(0,0));target.paste(S.crop((0,115,1254,742)),(0,627))
p=D/'centered-native-context.png'
if p.exists():raise FileExistsError(p)
target.save(p)
prompt='''Use case: precise-object-edit. This1254x1254 image is a real native crop of one continuous hand-painted stone pedestal, long stone stair rail and steps. There is an accidental HORIZONTAL STITCH through the center at y627. Repair that local discontinuity as one continuous surface, especially the left side and inset grooves of the long pale railing at x650..1005.
The lower half is the correct finished neighboring artwork. Keep its geometry, stone tone and carving details in place. The upper half must smoothly continue those exact lower grooves, bevels and shadows: no lateral step in either groove, no sudden width change, no horizontal light/dark boundary, no zigzag contour. Blend by repainting the actual stone shading and groove structure in a narrow central region around y450..740, not by blurring. The rail's right outside edge around x1004 is already nearly aligned; preserve it and the existing stair rhythm. Preserve all left green carving and pale coping outlines, the plain upper pedestal face, camera, image borders and object scale. Do not introduce an ornamental cap or new panel on the long vertical inset.
Keep distant upper and lower portions unchanged, especially lower y900..1253. This is a local seam repair with substantial genuine content on both sides, not a new scene. Clean smooth softly rounded hand-painted pale stone, gentle warm-grey stair risers, existing bright daylight. No text, UI, characters, new objects, watermark or reframing. Return the same fully opaque1254x1254 native crop.'''
params={'prompt':prompt,'referenced_image_paths':[str(p)],'transparent_background':False}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
record={'kind':'centered_native_context_guide','file':str(p),'sha256':sha(p),'pixels':[1254,1254],'worldBox':[12173,15757,13427,17011],
        'formalNorthSouthWorldY':16384,'formalSeamLocalY':627,'nativeOverlapWorldY':[16269,16499],
        'sources':[{'file':str(north),'sha256':sha(north),'sourceWorldBox':[12173,15245,13427,16499],'sourceCrop':[0,512,1254,1139],'targetBox':[0,0,1254,627]},
                   {'file':str(south),'sha256':sha(south),'sourceWorldBox':[12173,16269,13427,17523],'sourceCrop':[0,115,1254,742],'targetBox':[0,627,1254,1254]}],
        'operation':'Exact native crops pasted at true world coordinates; no source resampling or art drawn by code','gameArt':False,
        'plannedOutputWorldBox':[12173,15757,13427,17011],'plannedNorthernCoreContributionLocalY':[0,627],
        'southFileWillRemainUnmodified':True,'actualModel':None,'actualQuality':None}
(D/'preparation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
(D/'parameters.json').write_text(json.dumps(params,indent=2),encoding='utf-8');(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps({'parameters':str(D/'parameters.json'),'guide':str(p),'worldBox':record['worldBox']},indent=2))
