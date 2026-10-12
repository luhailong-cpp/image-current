from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
from PIL import Image

stem='r10_c03_c04_finial_upper_join_v01'; box=[11660,37300,12914,38554]
guide=ROOT/'guides'/f'{stem}.native-repair.png'
assert not guide.exists() and not (ROOT/'prompts'/f'{stem}.request.json').exists()
canvas=Image.new('RGB',(1254,1254)); sources=[]
entries=[('r10_c03_s01_04_v02',[11660,37300,12288,37888]),('r10_c04_s01_01_v01',[12288,37300,12914,37888]),('r10_c03_s02_04_v01',[11660,37888,12288,38554]),('r10_c04_s02_01_v01',[12288,37888,12914,38554])]
for stemin,lim in entries:
    p=ROOT/'native'/f'{stemin}.png'; b=load(str(p)+'.generation.json')['coordinates']['nativeGlobalBox']
    crop=[lim[0]-b[0],lim[1]-b[1],lim[2]-b[0],lim[3]-b[1]]; dest=[lim[0]-box[0],lim[1]-box[1]]
    with Image.open(p) as im: canvas.paste(im.crop(crop),dest)
    sources.append({**metadata(p,'native same-coordinate guide input'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
dump(str(guide)+'.derivation.json',{'createdAtUtc':now(),'file':str(guide),'sha256':hashfile(guide),'operation':'same-coordinate native hard crop/paste; no resampling, blending or art drawing','globalBox':box,'derivedFrom':sources})
co={'tiles':['r10_c03','r10_c04'],'kind':'existing golden roof finial upper half material continuity repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
refs=[metadata(guide,'fixed native gold roof finial EDIT TARGET')]+[metadata(*r) for r in REFS]
prompt='''Use case: precise-object-edit. Output exactly 1254 by 1254 pixels, opaque native square.
Image 1 is the fixed-coordinate edit target: the existing golden gourd-shaped pavilion roof finial, with tiny round tip, upper rounded lobe, narrow collar, and upper part of a second lobe at the bottom crop edge. Remove artificial vertical and horizontal patch seams in its golden material at x628 and y588. Make the entire round gold surface continuous, with coherent existing upper-left warm highlights, rounded painted facets, amber side shadows and fine crisp brush marks. Continue the light and grain across the centerline smoothly without a stripe. The round tip, main lobe and collar are a single existing ornament; do not add any new lobe, curl, hole, emblem or ornament.
Strictly preserve the exact silhouette, dimensions, locations and perspective of all gold parts. Preserve the natural worn courtyard stone slab joints, sparse tiny grass and paving outside it. Fix only artificial material block boundaries, with no blur, feather stripe, new objects, extra plants or design change. Everything stays sharply detailed at the original camera scale. Image 2 is the only full map layout reference; image 3 is independent material style only; image 4 is approved Chinese Daoist Q painterly style, no UI or scene transfer. Keep the existing daylight and gold palette, stone positions, framing and pixel coordinate extent. No text, watermark, grid, border or vignette.'''
(ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(str(guide))
