from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
from PIL import Image

stem='r09_r10_c03_steps_join_v01';box=[11034,36280,12288,37534]
guide=ROOT/'guides'/f'{stem}.native-repair.png'
assert not guide.exists() and not (ROOT/'prompts'/f'{stem}.request.json').exists()
canvas=Image.new('RGB',(1254,1254)); sources=[]
entries=[('output/r09_c03-native-candidate-v05.png',[8192,32768,12288,36864],[11034,36280,12288,36864])]
for s,lim in [('r10_c03_s01_03_v01',[11034,36864,11264,37534]),('r10_c03_s01_04_v02',[11264,36864,12288,37534]),('r09_r10_c04_steps_join_v01',[12173,36280,12288,37534])]:
    p=ROOT/'native'/f'{s}.png';entries.append((str(p),load(str(p)+'.generation.json')['coordinates']['nativeGlobalBox'],lim))
for name,b,lim in entries:
    p=ROOT/name;crop=[lim[0]-b[0],lim[1]-b[1],lim[2]-b[0],lim[3]-b[1]];dest=[lim[0]-box[0],lim[1]-box[1]]
    with Image.open(p) as im: canvas.paste(im.crop(crop),dest)
    sources.append({**metadata(p,'native same-coordinate guide input; last entry is corrected right stair overlap'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
dump(str(guide)+'.derivation.json',{'createdAtUtc':now(),'file':str(guide),'sha256':hashfile(guide),'operation':'same-coordinate native hard crop/paste; rightmost115 from adjacent stair native AI repair; no resampling or blending','globalBox':box,'derivedFrom':sources})
co={'tiles':['r09_c03','r10_c03'],'kind':'left stair whole-material junction repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
refs=[metadata(guide,'fixed native stair EDIT TARGET; rightmost115 already repaired adjacent native constraint')]+[metadata(*r) for r in REFS]
prompt='''Use case: precise-object-edit. Output exactly 1254 by 1254 pixels, opaque square native map artwork.
Image 1 is the fixed-coordinate stone stair edit target. Remove the artificial horizontal rectangular tone seam at y584 across the stone stair, the left stone supporting side and riser, and any small vertical tone patch at x230. Render the existing stone structure with coherent natural cream-gray mineral facets, warm light and continuous dappled shadows. Keep the entire geometry absolutely fixed: step edges, slab joints, stone corners, all object positions and their silhouettes. The far right115 pixels are already-corrected adjacent artwork and provide exact color, texture and geometry continuity; preserve these pixels and smoothly continue their stone appearance toward the left. Do not shift/crop/resize the stairs or introduce new geometry.
Use sharp native painterly detail with organic mineral marks, subtle wear and small cracks. No blurred band, airbrush stripe, new plants, flowers, posts, signs, props, decorations, figures or extra debris. Keep surrounding paving and any existing red/gold structure unchanged. Image 2 is the sole whole-map layout reference. Image 3 is independent material/style only. Image 4 is approved Chinese Daoist Q painterly style only, no UI or scene transfer. Preserve daylight, palette and native camera scale. No text, grid, frame, watermark or vignette.'''
(ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(str(guide))
