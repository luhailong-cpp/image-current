from pathlib import Path
import json
from PIL import Image
import tile_native_workflow as w
T=w.ZONE/'r12_c10';S=T/'repairs';S.mkdir(exist_ok=True)
stem='stairs-joint-p11-p21-v1';box=[36749,45615,38003,46869]
im=Image.new('RGB',(1254,1254));sources=[]
items=[('r12_c10','p11','native/p11-v3.png'),('r12_c10','p21','native/p21-v1.png'),('r12_c09','p14','processed/colorpass/p14-colorpass.png'),('r12_c09','p24','processed/colorpass/p24-colorpass.png')]
for tn,pid,rel in items:
 p=w.patch(w.read(w.ZONE/tn/'coordinate-plan.json'),pid);gb=p['globalBox'];b=[max(gb[0],box[0]),max(gb[1],box[1]),min(gb[2],box[2]),min(gb[3],box[3])]
 if b[0]>=b[2] or b[1]>=b[3]:continue
 src=w.ZONE/tn/rel;crop=[b[0]-gb[0],b[1]-gb[1],b[2]-gb[0],b[3]-gb[1]]
 im.paste(Image.open(src).crop(crop),(b[0]-box[0],b[1]-box[1]));sources.append({'path':str(src),'sha256':w.sha(src),'sourceBox':crop,'worldBox':b})
out=S/(stem+'-input.png');im.save(out)
w.write(out.with_suffix('.png.derivation.json'),{'operation':'unscaled exact-coordinate joint composite; west original selected native strip overrides overlap','globalBox':box,'sources':sources,'resamplingApplied':False})
prompt='''Precise native geometry repair, exactly 1254 x 1254 pixels. Image 1 is the exact world joint box [36749,45615,38003,46869] joining the stone landing above and the existing broad stone stairs below. Image 2 layout only, Image 3 daylight material only, Image 4 primary rounded clean painterly Q Daoist game style only. Keep scale and camera.
Repair the broken stone stair geometry across the entire image. The three long stair noses must each continue in one straight, uninterrupted diagonal toward the upper right, with no L-shaped sideways turns or vertical offsets in the middle. Preserve the exact positions and scale of the existing stair edges in the far LEFT 115 pixels, which join another finished map tile. The shallow pale band in the upper half belongs to the upper landing edge: reconcile it with the first broad stair and the full high riser entering from the left, so the result is one coherent flight, not four separate steps. Rebuild the lower half of the landing as necessary to accommodate the real stair height. Preserve the upper 100-pixel strip and its large grey paving slabs. Keep all stair edge endpoints on the left. Continue the stairs beyond the right and bottom crop as required; do not invent a stair end or side wall in the middle. Remove the three current staggered block ends at x275,395,500 completely. Whole broad crisp planar treads and rounded cream-grey stone risers with natural thin bevels, no melted transitions, no blur, no new posts, no rails, no props. Retain native large slab scale, fine painted material and daytime light. This is an extreme close-up of continuous map terrain, not an overview scene. No text, UI, watermarks or borders.'''
refs=[str(out)]+[r['path'] for r in w.approved_refs()]
(S/(stem+'.prompt.txt')).write_text(prompt,encoding='utf-8')
w.write(S/(stem+'.request.json'),{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':{'1':'native landing/stairs joint exact-coordinate edit target','2':'layout only','3':'daylight material only','4':'primary approved painterly style only'},'submittedParameters':{'model':None,'quality':None},'coordinate':{'globalBox':box,'dimensions':[1254,1254]}})
print(json.dumps({'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}))
