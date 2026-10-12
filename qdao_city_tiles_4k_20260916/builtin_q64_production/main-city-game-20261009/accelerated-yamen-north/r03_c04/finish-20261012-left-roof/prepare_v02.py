from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent;V=O/'v02';V.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((O/'v01/preparation.json').read_text())
im=Image.open(O/'v01/context-native.png').convert('RGB');im.save(V/'context-native.png')
mask=im.convert('RGBA');mask.paste((0,0,0,0),(130,545,490,690));mask.save(V/'edit-guide-transparent.png')
prompt='''Precise local image restoration. This is a 1254 by 1254 original-pixel texture. Return the opaque repaired image at exactly 1254 by 1254. Image 1 is the edit target with ONE transparent hole: x130..490, y545..690. Image 2 is the same original complete target, showing the faulty triangular ceramic flap that must be fixed inside that hole. FILL ONLY THAT HOLE using its surrounding pixels as rigid anchors.

The turquoise curved roof tiles are stylized glazed clay. Restore only this small broken lip. Connect the upper and lower visible gutter endpoints exactly where they meet the hole, using a smooth short curved transition if necessary. The lower row is staggered relative to the upper row: KEEP THAT STAGGER AND ITS EXACT TILE COUNT. Do NOT straighten it into matching vertical columns. Keep every lower tile boundary and bright stripe under y690 at its existing x position, keep every upper tile boundary above y545 at its existing x position. Draw the repaired cap with one smooth rounded edge. Remove the torn triangle and double overlap. Match the existing saturated cyan texture, dark navy gutter and white glossy highlights. Preserve the rest of the image, including remaining unrepaired junctions to the right; this job is ONLY the one transparent hole. No camera change, rotation, scaling, expansion, new tiles, sky or words.'''
params={'prompt':prompt,'referenced_image_paths':[str(V/'edit-guide-transparent.png'),str(V/'context-native.png')],'transparent_background':False}
(V/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8');(V/'prompt.txt').write_text(prompt,encoding='utf-8')
p.update(repairContextBox=[130,545,490,690],referenceSources=[{'file':f,'sha256':sha(Path(f))} for f in params['referenced_image_paths']],generationEditWindow=[130,545,490,690])
(V/'preparation.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'v01/visual-review.json').write_text(json.dumps({'verdict':'FAIL_DO_NOT_APPLY','actuallyViewed':True,'finding':'The new roof regularizes tile count below the window; after local compositing gutters shift by tens of pixels at the lower edge. No part selected.','inFlight':False},indent=2),encoding='utf-8')
print(V)
