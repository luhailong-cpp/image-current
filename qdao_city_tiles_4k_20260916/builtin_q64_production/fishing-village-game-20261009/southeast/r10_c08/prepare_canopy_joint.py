from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
stem='canopy-edge-joint-v1'
source=T/'processed/bench-rim-v1/candidate-4096.png'
box=[31117,38285,32371,39539]
target=T/'repairs'/f'{stem}-input.png'
crop=[box[0]-28672,box[1]-36864,box[2]-28672,box[3]-36864]
Image.open(source).crop(crop).save(target)
write(target.with_suffix('.png.derivation.json'),{'source':str(source),'sourceSha256':sha(source),'crop':crop,'globalBox':box,'sha256':sha(target),'resamplingApplied':False})
req=json.loads((T/'repairs/bench-rim-joint-v1.request.json').read_text())
req['referenced_image_paths'][0]=str(target)
req['referenceRoles']['1']='Exact native canopy and hull joint repair target, not layout enlargement'
req['coordinate']['globalBox']=box
write(T/'repairs'/f'{stem}.request.json',req)
prompt='''Use case: precise-object-edit. Image1 is the exact native 1254-square repair target. Restore the small soft section at local x627..992, y533..627: the ivory woven canopy seam and curved honey-gold wooden frame just above the central horizontal source join. Continue the existing sharp woven threads, stitched edge, woodgrain and rounded highlighted timber into this currently blurry section. Make the entire canopy/wood contour consistently finished and crisp. Preserve the original contour, perspective, composition and every object exactly. Do not move the curved frame, boat side rail, rear deck planks or fabric; do not add a rib or change dimensions. Keep the remaining image and outer 200 pixels unchanged, as this is part of a larger map. Image2 is map layout only; image3 is independent daylight material style only; image4 is the approved user Daoist Q style only, do not copy UI, lettering, night lighting or people. Bright clean daytime hand-painted rounded Q game art, native fine material detail. Exact world box [31117,38285,32371,39539], same zoom and camera, no scale or position changes. No blurry bands, no sharpening halo, no crossfade, no new object, no text, labels, frame or grid. Output the edited Image1 only.'''
(T/'repairs'/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps({'request':str(T/'repairs'/f'{stem}.request.json'),'input':str(target)}))
