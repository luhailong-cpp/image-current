from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix11_centered';D.mkdir(exist_ok=False)
source=B/'fix09_centered/centered-native-context.png';im=Image.open(source).convert('RGB');boxes=[(638,120,792,627),(897,370,934,627)]
for b in boxes:ImageDraw.Draw(im).rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=(255,0,255))
guide=D/'centered-repair-mask.png';im.save(guide)
prompt='''Fill the two magenta holes with the missing parts of this stone railing. The broad left hole is the COOL GRAY LEFT SIDE FACE of the rail: continue the gray face that touches the hole at its bottom edge upward through the whole hole. The narrow right hole is the thin straight inset groove: continue it upward accurately. Do not leave a horizontal color boundary across either filled hole. The surrounding image is finished artwork; preserve it. Same native 1254x1254 image, same geometry, no new objects, no magenta remaining. The result must look like one continuous piece of carved stone, with no seam at the horizontal center.'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
params={'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False}
rec={'worldBox':[12173,15757,13427,17011],'formalSeamLocalY':627,'width':1254,'height':1254,'baseFile':str(source),'baseSha256':sha(source),'baseProvenance':str(B/'fix09_centered/preparation.json'),'maskBoxes':boxes,'maskRGB':[255,0,255],'guideFile':str(guide),'guideSha256':sha(guide),'operation':'Native guide pixels plus solid repair masks only; no code-painted content may enter final','actualModel':None,'actualQuality':None}
for name,data in [('parameters.json',params),('preparation.json',rec)]: (D/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(str(D))
