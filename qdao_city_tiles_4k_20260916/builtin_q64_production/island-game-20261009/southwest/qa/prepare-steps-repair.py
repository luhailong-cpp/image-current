from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
from PIL import Image

stem='r09_r10_c04_steps_join_v01'; box=[12173,36280,13427,37534]
guide=ROOT/'guides'/f'{stem}.native-repair.png'
assert not guide.exists() and not (ROOT/'prompts'/f'{stem}.request.json').exists()
canvas=Image.new('RGB',(1254,1254)); sources=[]
entries=[('output/r09_c03-native-candidate-v05.png',[8192,32768,12288,36864],[12173,36280,12288,36864]),('output/r09_c04-native-candidate-v01.png',[12288,32768,16384,36864],[12288,36280,13427,36864])]
for s,lim in [('r10_c03_s01_04_v02',[12173,36864,12288,37534]),('r10_c04_s01_01_v01',[12288,36864,13312,37534]),('r10_c04_s01_02_v02',[13312,36864,13427,37534])]:
    p=ROOT/'native'/f'{s}.png'; entries.append((str(p),load(str(p)+'.generation.json')['coordinates']['nativeGlobalBox'],lim))
for name,b,lim in entries:
    p=ROOT/name; crop=[lim[0]-b[0],lim[1]-b[1],lim[2]-b[0],lim[3]-b[1]]; dest=[lim[0]-box[0],lim[1]-box[1]]
    with Image.open(p) as im: canvas.paste(im.crop(crop),dest)
    sources.append({**metadata(p,'native same-coordinate guide input'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
dump(str(guide)+'.derivation.json',{'createdAtUtc':now(),'file':str(guide),'sha256':hashfile(guide),'operation':'same-coordinate native hard crop/paste; no resampling, blending or art drawing','globalBox':box,'derivedFrom':sources})
co={'tiles':['r09_c03','r09_c04','r10_c03','r10_c04'],'kind':'shared stone stair whole-material junction repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
refs=[metadata(guide,'fixed native stair and pavement EDIT TARGET')]+[metadata(*r) for r in REFS]
prompt='''Use case: precise-object-edit. Output exactly 1254 by 1254 pixels, opaque square native artwork.
Image 1 is a fixed-coordinate Chinese Daoist Q painterly game-map close-up of pale stone steps and courtyard. Remove the artificial horizontal and vertical rectangular material seams crossing the step riser, treads and paving. The principal horizontal splice is y584 in the target, and vertical splices x115 and x1139. Continue the natural cream-gray stone colors, small painted mineral facets, mottling, reflected light and dappled shadows seamlessly across those lines. Treat the entire step as one coherent stone structure; no blurry seam stripe or box-shaped replacement. This is a material continuity repair, not a redesign.
Strictly preserve the existing straight step edges, slab joint locations, step thickness and perspective. Preserve every object silhouette and the tiny clipped gold finial if visible near the bottom. Keep all native detail sharply painted at this scale, natural organic stone texture, subtle tiny cracks and warm daylight. No plants, flowers, props, rails, posts, added ornament, new debris, text, watermarks or UI. Do not move, crop, stretch, warp or change the camera. Image 2 is the sole full map layout reference. Image 3 is material/style only, not a coordinate crop. Image 4 is the approved Daoist Q style only; no scene or UI transfer. Preserve the target composition and all geometry exactly while fixing the artificial block tone boundaries.'''
(ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(str(guide))
