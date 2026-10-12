from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
from PIL import Image

stem='r10_c03_c04_finial_lower_join_v01';box=[11660,39290,12914,40544]
guide=ROOT/'guides'/f'{stem}.native-repair.png';assert not guide.exists() and not (ROOT/'prompts'/f'{stem}.request.json').exists()
canvas=Image.new('RGB',(1254,1254));sources=[]
entries=[('r10_c03_s03_04_v01',[11660,39290,12288,39936]),('r10_c04_s03_01_v03',[12288,39290,12914,39936]),('r10_c03_s04_04_v01',[11660,39936,12288,40544]),('r10_c04_s04_01_v01',[12288,39936,12914,40544])]
for n in ['r10_c04_wallbase_col12_join_v01','r10_c03_c04_finial_middle_join_v01']:
    b=load(ROOT/'native'/f'{n}.png.generation.json')['coordinates']['nativeGlobalBox'];entries.append((n,[max(b[0],box[0]),max(b[1],box[1]),min(b[2],box[2]),min(b[3],box[3])]))
for n,lim in entries:
    p=ROOT/'native'/f'{n}.png';b=load(str(p)+'.generation.json')['coordinates']['nativeGlobalBox'];crop=[lim[0]-b[0],lim[1]-b[1],lim[2]-b[0],lim[3]-b[1]];dest=[lim[0]-box[0],lim[1]-box[1]]
    with Image.open(p) as im:canvas.paste(im.crop(crop),dest)
    sources.append({**metadata(p,'same-coordinate native guide source; later repaired source has priority'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
co={'tiles':['r10_c03','r10_c04'],'kind':'emerald and gold roof pedestal shared material join','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co);dump(str(guide)+'.derivation.json',{'file':str(guide),'sha256':hashfile(guide),'operation':'same-coordinate native hard crop/paste; no resampling or painting','coordinates':co,'derivedFrom':sources})
refs=[metadata(guide,'fixed native gold and jade roof pedestal EDIT TARGET; corrected top284 constraint')]+[metadata(*r) for r in REFS]
prompt='''Use case: precise-object-edit. Output exactly1254 by1254 pixels, opaque native square.
Image1 is the fixed-coordinate lower section of the existing pavilion roof finial: golden round base, emerald jade inset panels, curved gold ribs, orange-gold lower fascia and any blue glazed tiles. Fix the artificial vertical material division at x628 and horizontal patch tone boundaries around y646. Make jade grain, warm gold brushwork and highlights coherent across those seams. The top284 pixels come from the repaired upper section; keep that corrected native color and geometry as the exact adjoining context. Continue the existing rounded ring, jade panels, ribs and fascia without abrupt color boxes or contour steps.
Preserve all object positions, outlines, thickness, perspective, curved shape, green inset borders and tile directions exactly. Do not add ribs, ornaments, loops, holes, new objects, plants or text. Native sharp Daoist Q painterly map detail, warm daylight, original green/blue/gold palette. No blur stripe or soft masking. Image2 is sole full map layout reference. Image3 is independent material/style only; image4 is approved Daoist Q style only, no UI or scene transfer. No crop, warp, scale, camera change, watermark, border or vignette.'''
(ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8');dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(str(guide))
