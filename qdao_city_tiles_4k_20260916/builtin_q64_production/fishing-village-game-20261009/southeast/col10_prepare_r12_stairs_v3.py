from pathlib import Path
import json
from PIL import Image,ImageFilter
import tile_native_workflow as w
T=w.ZONE/'r12_c10';S=T/'repairs';stem='stairs-joint-p11-p21-v3'
old=S/'stairs-joint-p11-p21-v1-input.png';src=Image.open(old);im=src.filter(ImageFilter.GaussianBlur(42));im.paste(src.crop((0,0,1254,100)),(0,0));im.paste(src.crop((0,0,230,1254)),(0,0));out=S/(stem+'-input.png');im.save(out)
w.write(out.with_suffix('.png.derivation.json'),{'operation':'conditioning only; exact west230 and top100 preserved, remaining wrong topology blurred as layout-only','source':str(old),'sha256':w.sha(old),'globalBox':[36749,45615,38003,46869],'finalPixelsMayBeUsed':False})
q=w.read(S/'stairs-joint-p11-p21-v2.request.json');q['referenced_image_paths'][0]=str(out)
q['prompt']='''Finish one native 1254 x 1254 close-up game-map patch. Image 1 is a sharp LEFT strip plus TOP strip, the remaining area blurred for replacement. Strictly retain every sharp left-strip contour and continue it smoothly through the new interior at original size. Do not copy the blurred area. Image 2 is full-map layout only; image 3 daylight material style; image 4 primary clean rounded Q Daoist painterly style only.
There are FOUR separate light stone bands entering from the left: a narrow curb at y480, a tall riser whose top is y690 and bottom y870, a tall riser whose top is y1000 and bottom y1190, and part of a final riser below the bottom edge. Keep ALL of these existing bands at those heights, including the tall riser immediately BELOW the shallow curb. Continue EVERY one straight diagonally upward-right across the image. Continue the thin grey treads between them. These four separate bands must not be merged or deleted. Preserve the sharp left 230 pixels as immutable registration geometry. Do not create staggered ends, L-shaped corners, exposed stair ends, walls, posts, or miniatures. Let the steps extend out of the crop. The broad landing above remains grey blue natural stone at the same native large slab scale. Upper100 pixels unchanged. Clear continuous crisp beveled stone forms and fine painted detail. No blur, text, UI or watermarks.'''
(S/(stem+'.prompt.txt')).write_text(q['prompt'],encoding='utf-8');w.write(S/(stem+'.request.json'),q)
print(json.dumps({k:q[k] for k in ['prompt','referenced_image_paths','transparent_background']}))
