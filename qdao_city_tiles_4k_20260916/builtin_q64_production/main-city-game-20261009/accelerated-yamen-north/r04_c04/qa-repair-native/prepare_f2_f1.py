from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent;T=D.parent;C=T/'candidate/r04_c04-pipeline-minimum-error-fbb8f7edb616-fe50f8.png';im=Image.open(C).convert('RGB')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(C)=='d2a7884de15f115597edc3ba27007a2ccfe1cba0b0935c239679d6a9abf0db1b'
jobs=[
 ('f2-rail-tone',[0,2544,1254,3798],[603,3157,644,3187],'''Use case: precise-object-edit. Repair the small accidental diagonal COLOR PATCH on the slim cool-gray side face of the pale stone railing near the CENTER of this 1254x1254 crop, around x605..645, y610..645. That long narrow gray face should have continuous gentle stone shading. Remove its sudden diagonal light/dark cut without blurring the stone. Keep the exact existing outside edges, cream bevels, dark inset grooves, slab joints and their positions. This is a local material/shading repair only: the geometry is already aligned. Match the adjacent intact gray stone above and below. Preserve every surrounding wall, stair, rail, lighting direction and image framing. No extra geometry, no reframing, no text or object. Same fully opaque 1254x1254 native image.'''),
 ('f1-door-groove',[1870,423,3124,1677],[2492,1038,2503,1061],'''Use case: precise-object-edit. This is a native close crop of a wooden doorway. Repair ONLY the tiny sideways kink in the fine dark vertical wooden plank groove near the image center, around x625,y627. Its upper and lower portions should join as one slender continuous wood joint, without the current 3–4 pixel sideways step in its dark line and highlight. Keep the neighboring wood grain, warm reddish-brown material, plank widths, door frame and red-gold decoration unchanged. Make a local geometric correction over a modest length above and below the kink so the joint flows naturally into the unchanged groove. Do not blur or paint over the groove. No new groove, no thicker line, no new objects. Same fully opaque 1254x1254 native crop and scale.''')]
for name,box,defect,prompt in jobs:
 O=D/name;O.mkdir(exist_ok=False);p=O/'context-native.png';im.crop(box).save(p)
 params={'prompt':prompt,'referenced_image_paths':[str(p)],'transparent_background':False}
 rec={'baseFile':str(C),'baseSha256':sha(C),'contextTileBox':box,'contextWorldBox':[x+12288 for x in box],'width':1254,'height':1254,'sourceOperation':'Exact original pixel crop, no resampling','defectTileBoxApprox':defect,'contextFile':str(p),'contextSha256':sha(p),'actualModel':None,'actualQuality':None}
 (O/'parameters.json').write_text(json.dumps(params,indent=2),encoding='utf-8');(O/'preparation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8');(O/'prompt.txt').write_text(prompt,encoding='utf-8')
 print(str(O))
