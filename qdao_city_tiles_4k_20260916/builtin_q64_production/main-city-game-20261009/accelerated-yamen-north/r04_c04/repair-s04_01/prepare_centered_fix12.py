from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix12_centered';D.mkdir(exist_ok=False)
north=B/'fix11_centered/generated-centered.png';south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
N=Image.open(north).convert('RGB');S=Image.open(south).convert('RGB');base=Image.new('RGB',(1254,1254));base.paste(N.crop((0,0,1254,512)),(0,0));base.paste(S.crop((0,0,1254,742)),(0,512));base.save(D/'centered-native-context.png')
im=base.copy();boxes=[(638,120,793,512),(895,320,935,512)]
for b in boxes:ImageDraw.Draw(im).rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=(255,0,255))
guide=D/'centered-repair-mask.png';im.save(guide)
prompt='''Fill the two magenta holes with the missing parts of this stone rail. Continue the cool gray LEFT BEVEL and its fine straight inset groove from immediately BELOW the holes upward, matching their exact horizontal locations and shades. Fill the right hole with the continuation of the existing right groove. Keep the image outside the two holes unchanged, especially everything below y512. The lower 742 rows are the finished original artwork; the missing upper parts must fit THAT artwork. Do not reposition, widen, narrow, recolor or redraw the grooves below the holes. No new ornamental carving, no blur. Restore a continuous rail with consistent geometry and no seam. Same fully opaque 1254x1254 native image and framing.'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
params={'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False}
rec={'worldBox':[12173,15757,13427,17011],'formalSeamLocalY':627,'sourceJoinLocalY':512,'width':1254,'height':1254,
 'sources':[{'file':str(north),'sha256':sha(north),'worldBox':[12173,15757,13427,17011],'crop':[0,0,1254,512],'targetBox':[0,0,1254,512]}, {'file':str(south),'sha256':sha(south),'worldBox':[12173,16269,13427,17523],'crop':[0,0,1254,742],'targetBox':[0,512,1254,1254]}],
 'maskBoxes':boxes,'maskRGB':[255,0,255],'guideFile':str(guide),'guideSha256':sha(guide),'operation':'True-world native crop/paste plus guide-only repair masks; no resampling','actualModel':None,'actualQuality':None}
for name,data in [('parameters.json',params),('preparation.json',rec)]: (D/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(str(D))
