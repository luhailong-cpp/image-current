from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import ROOT, REFS, load, dump, metadata, hashfile, now
from PIL import Image

stem='r10_c03_railing_join_v01'
box=[9650,38797,10904,40051]
guide=ROOT/'guides'/f'{stem}.native-repair.png'
request=ROOT/'prompts'/f'{stem}.request.json'
assert not request.exists() and not guide.exists() and not (ROOT/'native'/f'{stem}.png').exists()
canvas=Image.new('RGB',(1254,1254))
sources=[]
for source,limits in [('r10_c03_s03_02_v02',[9650,38797,10240,40051]),('r10_c03_s03_03_v02',[10240,38797,10904,40051])]:
    p=ROOT/'native'/f'{source}.png'
    rec=load(str(p)+'.generation.json'); b=rec['coordinates']['nativeGlobalBox']
    crop=[limits[0]-b[0],limits[1]-b[1],limits[2]-b[0],limits[3]-b[1]]
    dest=[limits[0]-box[0],limits[1]-box[1]]
    with Image.open(p) as im: canvas.paste(im.crop(crop),dest)
    sources.append({**metadata(p,'same-coordinate native guide source'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
dump(str(guide)+'.derivation.json',{'file':str(guide),'sha256':hashfile(guide),'createdAtUtc':now(),'operation':'native same-coordinate hard crop/paste; no scaling, blending or art drawing','globalBox':box,'derivedFrom':sources})
co={'tile':'r10_c03','kind':'whole stone railing junction geometry repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
refs=[metadata(guide,'EDIT TARGET: fixed same-coordinate native stone railing join'),metadata(ROOT/'guides/r10_c03-lower-left-context-layout-only.png','whole pavilion original layout context only')]+[metadata(*r) for r in REFS]
prompt='''Use case: precise-object-edit. Output exactly 1254 by 1254 pixels, opaque square native map artwork.
Image 1 is the edit target: a fixed-coordinate native close-up of the original courtyard stone railing and blue pavilion roof. Fix the small vertical break at x590 in this crop: the pale stone top cap and the two horizontal stone beams below must each run as one coherent gently rising line across the entire image, with their thickness, lower edges, shadows and side faces joining smoothly. Repair the full railing structure as one object, including the low stone base immediately above the blue roof. The left and right sides show the same continuous rail, not different rails or additional rails. Align their 15-35 pixel offsets through a gradual physically straight perspective line; remove abrupt steps and light/dark blocks. Preserve the far-left and far-right endpoints and all existing stone posts. No bending, double rails, extra supports or new objects.
The blue glazed roof courses and golden roof edge are existing elements: keep their placement, direction, contours, palette and native sharpness unchanged. Preserve the courtyard stone paving above. Do not insert any gold spiral/scroll, decoration, plant, flower, lantern, sign, figure or text. Original image 2 gives pavilion layout only; image 3 is the sole full-map layout reference. Images 4 and 5 are material/style only. Use the same approved daylight Chinese Daoist Q painterly map appearance, detailed natural worn stone, crisp small-scale edges, organic brush grain, no shallow focus. Do not copy other buildings or UI from the references. Do not shift the camera, crop, scale, borders or architecture. Change only the railing junction geometry and directly associated shading/material needed to make it continuous. Retain the surrounding native detail. No border, grid, checkerboard, seam stripe, watermark or text.'''
(ROOT/'prompts'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
dump(request,{'tool':'image_gen.imagegen','references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(str(guide))
