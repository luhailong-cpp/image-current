from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;D=B/'fix13_centered';D.mkdir(exist_ok=False)
source=B/'fix12_centered/centered-native-context.png';im=Image.open(source).convert('RGB');boxes=[(635,120,796,610),(894,300,935,610)]
for b in boxes:ImageDraw.Draw(im).rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=(255,0,255))
guide=D/'centered-repair-mask.png';im.save(guide)
prompt='''Restore the two magenta missing areas of this pale stone railing. Reconstruct a continuous cool gray left bevel, bright raised edge, and thin recessed vertical grooves. Smoothly connect the intact stone at the TOP and BOTTOM edges of each hole. The groove and bevel on either side of each missing region must connect without a sideways step, notch, horizontal band or sudden color change. Preserve all visible pixels outside the missing regions as closely as possible. Especially preserve the existing geometry, colors and carving below the holes; that finished art determines the repair. Do not insert any new ornament, text or object. Return the same fully opaque 1254x1254 native crop, all magenta removed.'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
params={'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False}
rec={'worldBox':[12173,15757,13427,17011],'formalSeamLocalY':627,'sourceJoinLocalY':512,'width':1254,'height':1254,'baseFile':str(source),'baseSha256':sha(source),'baseProvenance':str(B/'fix12_centered/preparation.json'),'maskBoxes':boxes,'maskRGB':[255,0,255],'guideFile':str(guide),'guideSha256':sha(guide),'operation':'Native source crops plus guide-only masks crossing source join; no resampling','actualModel':None,'actualQuality':None}
for name,data in [('parameters.json',params),('preparation.json',rec)]: (D/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(str(D))
