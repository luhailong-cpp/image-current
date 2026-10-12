import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib,datetime
z=Path(__file__).resolve().parents[1];q=z/'qa';base=q/'pair-r08c06-r09c06-v1-context-native.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(base).convert('RGB')
jobs=[
('south_canopy',[300,3500,1554,4754],"Repair only the conspicuous accidental duplicated notch in the blue canopy left front corner at roughly x=310..420,y=560..760 and the chopped angular blue fold across x=600..1100,y=650..850. This is ONE continuous blue fabric canopy with ONE small cutout wrapping the gold-capped left support. The left corner must have just one smooth routed notch, not a doubled zigzag. The sloping front hem and its single stitch row flow continuously right/down. On the top blue fabric, connect the existing diagonal fold smoothly across the old horizontal image join; remove abrupt triangular chopped color steps, not the natural folds. Keep the existing gold cap, wooden horizontal beam, red support and stone pavement positions unchanged. Do not add, remove or shift objects. The top of the blue fabric is lighter geometric weave; blend its painted material naturally into the existing lower right fabric and preserve the exact outer-border contours."),
('south_lantern',[2957,3450,4211,4704],"Repair only the existing large red lantern across the obvious horizontal collage break in its LOWER HALF. Make ONE continuous rounded lantern: the thin red structural ribs must each continue in their existing trajectory down to the bottom gold collar, and the existing small gold cloud ornaments must be continuous whole decorations with no doubled or sliced fragment. Keep the exact red lantern silhouette, body size, bottom gold collar, red hanging cord and all surrounding blue cloth/wood architecture unchanged. Match the lantern's deep red left shade and bright orange right face without a horizontal color band. The right edge of the lantern intentionally crosses the image border; preserve that crossing exactly, do not complete the lantern or zoom out.")
]
out=[]
for rid,b,desc in jobs:
 stem='r08_c06_r09_c06_repair_'+rid+'_v1';cb=[v+115 for v in b];src=q/(stem+'-source-1254.png')
 assert not src.exists();im.crop(cb).save(src)
 prompt="Edit the attached exact 1254 x 1254 native crop, returning ONE 1254 x 1254 image at identical framing and scale. This is a local seamless restoration of bright hand-painted isometric game-map artwork. "+desc+" Preserve the whole outer 160-pixel border as an exact continuity anchor. No zoom, no crop, no reframing, no new objects, no text, no watermark, no blur or global lighting/color change."
 pp=z/'native'/(stem+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
 req={'stem':stem,'tile':'r08_c06/r09_c06','tool':'image_gen__imagegen','route':'builtin','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt':pp.as_posix(),'coordinates':{'tileContextBoxFromNorthTile':b,'pairContextBox':cb,'sourceContext':{'path':base.as_posix(),'sha256':sha(base)}},'references':[{'path':src.as_posix(),'sha256':sha(src),'dimensions':[1254,1254],'role':'exact native cross-tile seam edit target'}],'submittedParameters':{'transparent_background':False,'referenced_image_paths':[src.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None}
 rp=z/'native'/(stem+'.request.json');assert not rp.exists();rp.write_text(json.dumps(req,indent=2)+'\n',encoding='utf-8');out.append(req)
print(json.dumps(out))

