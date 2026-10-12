from pathlib import Path
import json,hashlib
from PIL import Image
import tile_native_workflow as w
T=w.ZONE/'r11_c10'
S=T/'repairs';S.mkdir(exist_ok=True)
stem='joint-p31-p32-p41-p42-v1'
box=[37261,43405,38515,44659]
plan=w.read(T/'coordinate-plan.json')
x,y=plan['tileOrigin']
src=T/'r11_c10-candidate-4096.png'
out=S/(stem+'-input.png')
Image.open(src).crop([box[0]-x,box[1]-y,box[2]-x,box[3]-y]).save(out)
w.write(out.with_suffix('.png.derivation.json'),{'operation':'unscaled native composite crop','source':str(src),'sha256':w.sha(src),'globalBox':box,'dimensions':[1254,1254],'resamplingApplied':False})
prompt="""Precise game-map geometry repair. Return exactly one 1254 by 1254 native pixel image at the identical camera and scale. Image 1 is the exact native four-patch crossing to repair, world box [37261,43405,38515,44659]. Image 2 is the map layout only; Image 3 daytime material style only; Image 4 primary approved rounded clean Q Daoist painterly style only, no text/UI/night imagery.
Repair the ENTIRE broken wood-platform to grey-stone transition visible across the middle of image 1. It currently has a square wood tab hanging down at the center plus mismatched stone slab T-junctions. Rebuild it as ONE coherent continuous naturally diagonal wooden platform boundary, with the grey stone apron below it, connected exactly to the existing boundary endpoints on left and right. Preserve the existing diagonal timber support end at upper left and all intact wooden board grooves at the top. Keep stone slab size, plane and perspective; reconnect all paver grooves through the central area without doubled edges or floating fragments.
The outer 100 pixels of all four edges are registration anchors: keep those exact surface types, boundary crossing coordinates, groove endpoints, color and lighting; fix connections through the full interior. No rectangular edit boundary, no blur, no new structures, objects, posts, rails, steps, paving borders, text or watermarks. Repaint native crisp geometry and texture; never smear or soften details. A slight rounded bevel on the wood edge only, not a new raised wall."""
refs=[str(out)]+[r['path'] for r in w.approved_refs()]
(S/(stem+'.prompt.txt')).write_text(prompt,encoding='utf-8')
w.write(S/(stem+'.request.json'),{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':{'1':'native four-patch exact-coordinate edit target','2':'layout only','3':'daylight material style only','4':'primary approved painterly style only'},'submittedParameters':{'model':None,'quality':None},'coordinate':{'globalBox':box,'dimensions':[1254,1254]}})
print(json.dumps({'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}))

