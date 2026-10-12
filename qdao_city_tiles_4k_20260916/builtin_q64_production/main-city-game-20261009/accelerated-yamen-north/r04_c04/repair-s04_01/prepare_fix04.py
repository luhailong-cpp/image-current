from pathlib import Path
from PIL import Image
import json,hashlib
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
D=BASE/'fix04';D.mkdir(parents=True,exist_ok=True)
south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
guide=BASE/'fix03/exact-south-context.png'
band=D/'real-south-top230.png'
if band.exists():raise FileExistsError(band)
Image.open(south).crop((0,0,1254,230)).save(band)
prompt='''Use case: precise-object-edit. Edit image 1, a 1254x1254 native hand-painted stone close-up. Image 2 is ONLY the correct bottom 230px of this same crop, cut directly from its real southern neighbor. It defines exact geometry to continue upward.
Repair the vertical stone rail in image 1 above the horizontal discontinuity at y1024: the upper rail is too wide on its right side. Make the whole long straight pale rail flow seamlessly into the correct bottom strip. At the join its RIGHT outside edge must be x1004, and its RIGHT inset groove x917. Keep its LEFT side and the large pedestal faces to the left in place. Narrow the upper rail from the right; fill the released area with the adjacent steps. The final rail is a single LONG UNBROKEN VERTICAL inset that crosses BOTH the top and bottom image borders. There must be NO end cap, no rounded inset ending, no little ornamental panel anywhere in this crop. It is only the mid-section of a much longer rail. Do not import objects from elsewhere.
Keep the entire bottom band y1024..1253 exactly like image 2, including rail position, green inset only beginning near the bottom, coping and stone colors. Bring the upper steps into the fixed lower steps with consistent rhythm, including the tread edge at y1132. Remove the accidental horizontal join through the rail by changing ONLY the upper geometry, never relocating the bottom reference.
Preserve composition, scale and camera; keep the large plain stone slab on the left, all correct coping and only the small green panel fragment at the very bottom. Smooth clean softly rounded pale stone in bright daylight. No new objects, no text, no UI, no people, no watermark. Return opaque square 1254x1254. This is a local geometry repair, not a redesign.'''
params={'prompt':prompt,'referenced_image_paths':[str(guide),str(band)],'transparent_background':False}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
(D/'parameters.json').write_text(json.dumps(params,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
(D/'preparation.json').write_text(json.dumps({'tile':'r04_c04','patch':'s04_01','version':'fix04','worldBoxWithHalo':[12173,15245,13427,16499],
'source':{'file':str(south),'sha256':sha(south),'crop':[0,0,1254,230]},'references':[{'file':str(p),'sha256':sha(p),'size':list(Image.open(p).size)} for p in [guide,band]],
'operation':'Exact real neighbor crop only; unscaled source pixels; no artwork rendered by code','actualModel':None,'actualQuality':None},indent=2),encoding='utf-8')
print(str(D/'parameters.json'))
