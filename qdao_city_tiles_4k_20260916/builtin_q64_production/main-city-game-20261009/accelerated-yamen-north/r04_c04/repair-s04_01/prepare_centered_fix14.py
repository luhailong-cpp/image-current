from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'fix14_centered';D.mkdir(exist_ok=False)
source=B/'fix12_centered/centered-native-context.png';sf=ROOT.parent/'northwest/r05_c04/native/s01_01.png';im=Image.open(source).convert('RGB');boxes=[(635,0,796,740),(895,250,935,680)]
for b in boxes:ImageDraw.Draw(im).rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=(255,0,255))
guide=D/'centered-repair-mask.png';im.save(guide);ref=D/'actual-south-rail-native.png';Image.open(sf).crop((640,0,1008,742)).save(ref)
prompt='''Use case: precise-object-edit. Image 1 is the edit target. Fill its magenta holes with a continuous long stone rail. Image 2 is a native crop of the correct LOWER rail in the same scene, for its exact cross-section and colors; it is not a new object to insert.
Continue the LOWER rail's sloping dark outside edge, cool gray side face, narrow cream bevel and recessed groove UP through the long missing strip. Follow the angle of those existing lines in the bottom half. Do not keep the wrong upper rail profile: the left bevel at the horizontal middle must sit farther RIGHT, continuing the lower gray face. At the center around y600, the dark outside boundary is about x695, gray face x696..726, light ridge near x734 and inner groove near x767. Match that correct lower geometry, not a narrower rail with ridge at x720. At the bottom of the missing strip, join the visible original rail without any step or color seam.
The smaller right hole is the thin inset groove near x917: restore it as a continuous line. Keep the large pale inset face, steps, left wall and green carving. Preserve visible pixels outside the holes as closely as possible. No extra ornaments. Same fully opaque 1254x1254 image and framing.'''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
params={'prompt':prompt,'referenced_image_paths':[str(guide),str(ref)],'transparent_background':False}
rec={'worldBox':[12173,15757,13427,17011],'formalSeamLocalY':627,'sourceJoinLocalY':512,'width':1254,'height':1254,'baseFile':str(source),'baseSha256':sha(source),'baseProvenance':str(B/'fix12_centered/preparation.json'),'maskBoxes':boxes,'maskRGB':[255,0,255],
 'references':[{'file':str(guide),'sha256':sha(guide),'role':'edit target with guide-only mask'}, {'file':str(ref),'sha256':sha(ref),'role':'supporting true south rail crop','source':str(sf),'sourceSha256':sha(sf),'sourceCrop':[640,0,1008,742],'worldBox':[12813,16269,13181,17011]}],
 'operation':'Native source crops plus guide-only masks; no resampling','actualModel':None,'actualQuality':None}
for name,data in [('parameters.json',params),('preparation.json',rec)]: (D/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(str(D))
