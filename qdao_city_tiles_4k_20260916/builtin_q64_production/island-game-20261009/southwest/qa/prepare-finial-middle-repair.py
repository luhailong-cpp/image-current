from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
from PIL import Image

stem='r10_c03_c04_finial_middle_join_v01';box=[11660,38320,12914,39574]
guide=ROOT/'guides'/f'{stem}.native-repair.png'
assert not guide.exists() and not (ROOT/'prompts'/f'{stem}.request.json').exists()
canvas=Image.new('RGB',(1254,1254));sources=[]
entries=[('r10_c03_s02_04_v01',[11660,38320,12288,38912]),('r10_c04_s02_01_v02',[12288,38320,12914,38912]),('r10_c03_s03_04_v01',[11660,38912,12288,39574]),('r10_c04_s03_01_v03',[12288,38912,12914,39574])]
for n in ['r10_c04_wall_col12_join_v01','r10_c04_wallbase_col12_join_v01','r10_c03_c04_finial_upper_join_v01']:
    b=load(ROOT/'native'/f'{n}.png.generation.json')['coordinates']['nativeGlobalBox']; entries.append((n,[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]))
for s,lim in entries:
    p=ROOT/'native'/f'{s}.png';b=load(str(p)+'.generation.json')['coordinates']['nativeGlobalBox'];crop=[lim[0]-b[0],lim[1]-b[1],lim[2]-b[0],lim[3]-b[1]];dest=[lim[0]-box[0],lim[1]-box[1]]
    with Image.open(p) as im:canvas.paste(im.crop(crop),dest)
    sources.append({**metadata(p,'same-coordinate native guide source; later repair source has priority'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
co={'tiles':['r10_c03','r10_c04'],'kind':'existing gold lower lobe and flared base material join','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
dump(str(guide)+'.derivation.json',{'file':str(guide),'sha256':hashfile(guide),'operation':'same-coordinate native hard crop/paste; no scaling, blending or art drawing','coordinates':co,'derivedFrom':sources})
refs=[metadata(guide,'fixed native gold finial middle EDIT TARGET; top234 are corrected upper source')]+[metadata(*r) for r in REFS]
prompt='''Use case: precise-object-edit. Output exactly1254 by1254 pixels, opaque native square.
Image1 is the fixed-coordinate native gold roof finial lower lobe and flared golden pedestal edit target. Remove the artificial vertical material split at x628 and horizontal patch tone transitions. The rounded gold lower lobe, collar and broad flared base must have uninterrupted painted gold grain, coherent bright warm highlights and amber shading across the central join. The upper234 pixels already include the corrected adjoining upper image; retain that material and geometry as the top context and continue smoothly downward. Do not alter any silhouette, curvature, ring thickness, emerald panel edge or existing beam position.
Preserve the original stone railing in the background, any green jade inset at the bottom, and the exact camera scale and positions. Only repair the artificial color/material divisions; no new joints, gold emblems, curls, ornamental parts, plants, extra rails, text or props. Keep the original daylight Chinese Daoist Q painterly style, sharp painted facets and no shallow-focus blur. Image2 is the sole full-map layout reference. Image3 is independent material/style only. Image4 is approved Daoist Q style only, no UI/scene transfer. Do not resize, warp, shift, crop or recolor the entire target. No softened seam stripe, border, watermark or vignette.'''
(ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(str(guide))
