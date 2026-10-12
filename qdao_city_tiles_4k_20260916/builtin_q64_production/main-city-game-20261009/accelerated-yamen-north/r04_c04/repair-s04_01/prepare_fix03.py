from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
T=ROOT/'r04_c04'
D=Path(__file__).resolve().parent/'fix03'
D.mkdir(parents=True,exist_ok=True)
current=T/'native/s04_01_fix02.png'
south=ROOT.parent/'northwest/r05_c04/native/s01_01.png'
guide=Image.open(current).convert('RGB')
old=Image.open(south).convert('RGB')
guide.paste(old.crop((0,0,1254,230)),(0,1024))
gp=D/'exact-south-context.png'
if gp.exists():raise FileExistsError(gp)
guide.save(gp)
prompt='''Use case: precise-object-edit.
Asset: one native 1254x1254 close crop of the existing continuous hand-painted stone staircase, not a whole building.
Image 1 is the EDIT TARGET. Its bottom 230 pixel band y=1024..1253 contains the exact correct adjacent artwork and MUST remain unchanged. Image 2 is the actual native SOUTH NEIGHBOR, reference only: its top 230 rows are the same world area as image 1 bottom 230 rows. Do not copy its whole scene into the target.
Task: repair ONLY the mismatching upper stone rail and adjacent right stairs in image 1 so that they flow perfectly into the fixed bottom band. The visible horizontal cut at y=1024 must vanish because the UPPER rail is repainted to match the LOWER rail. Above the cut the rail is too wide: its outer right silhouette is near x1064 but must meet the lower band at x1004; its inner right groove is near x963 but must meet the lower groove near x917. Bring the upper right silhouette and inner groove LEFT to these correct lower positions throughout the rail, while keeping the left silhouette and left groove anchored. The long pale rail should have one consistent width and smoothly continuous bevels, no sideways step, taper kink, offset groove, or horizontal color band. Right stairs start at the rail's right edge near x1004, not x1064. Repaint their cadence near the bottom so the existing lower tread edge at y1132 continues correctly, without a new step at y1109.
Preserve the exact image crop and pixel scale, the large simple pale pedestal faces on the left, the horizontal stone coping above the green panel, the green panel only peeking in at the bottom, and all correct bottom-band carved shapes. Keep softly rounded smooth pale stone, gentle warm grey risers, bright daylight and subtle clean hand-painted material identical to image 2. No additional object, text, people, UI or watermark. No camera shift, enlargement, rotation or reframe. Return one opaque 1254x1254 square.'''
params={'prompt':prompt,'referenced_image_paths':[str(gp),str(south)],'transparent_background':False}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
(D/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'prompt.txt').write_text(prompt,encoding='utf-8')
(D/'preparation.json').write_text(json.dumps({'tile':'r04_c04','patch':'s04_01','version':'fix03','worldBoxWithHalo':[12173,15245,13427,16499],
 'sourceImages':[{'file':str(p),'sha256':sha(p)} for p in [current,south]],'guide':{'file':str(gp),'sha256':sha(gp),'gameArt':False},
 'operation':'Exact native crop/paste only: south source [0,0,1254,230) to target [0,1024,1254,1254), no resampling',
 'actualModel':None,'actualQuality':None},indent=2),encoding='utf-8')
print(str(D/'parameters.json'))
