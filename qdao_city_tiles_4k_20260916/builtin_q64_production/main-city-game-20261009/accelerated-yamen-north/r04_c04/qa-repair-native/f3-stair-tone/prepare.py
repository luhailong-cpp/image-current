from pathlib import Path
import hashlib, json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'candidate/r04_c04-pipeline-minimum-error-fbb8f7edb616-fe50f8.png'
EXPECTED='d2a7884de15f115597edc3ba27007a2ccfe1cba0b0935c239679d6a9abf0db1b'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==EXPECTED
im=Image.open(BASE).convert('RGB')
for name,box,defect in [
 ('f3-stair-tone',[1499,2411,2753,3665],[2102,2987,2151,3090]),
 ('f4-stair-tone',[2449,2413,3703,3667],[3060,2990,3093,3091])]:
 out=ROOT/'qa-repair-native'/name
 out.mkdir(parents=True,exist_ok=True)
 guide=im.crop(box)
 assert guide.size==(1254,1254)
 guide.save(out/'guide-native.png')
 guide.save(out/'source-context.png')
 d=[defect[0]-box[0],defect[1]-box[1],defect[2]-box[0],defect[3]-box[1]]
 prompt=f'''Use case: precise-object-edit.
Edit target: the attached exact 1254 by 1254 pixel native crop of existing stylized game-art pale stone stairs. Output exactly 1254 by 1254 pixels, same framing, same coordinates, same scale, opaque RGB.
Primary request: repair ONLY the unnatural hard tonal patch boundary on the grey vertical face of the stair near the center, in the neighborhood of pixel box {d} (half-open coordinates from upper left). This is an unwanted compositing seam across a single continuous stone face, not a real stone joint. Make its local gray/taupe tone and subtle painted stone texture coherent across the patch boundary, preserving the surrounding natural shading. Let the repair blend naturally into the unchanged surrounding stone. The repair should be unobtrusive and keep the same artistic treatment.
Invariants: keep every horizontal stair edge, thin dark joint, bright bevel, tread/riser boundary, true block joint, object silhouette, row height, texture scale, camera and lighting at its exact current pixel location. Do not move, straighten, bend, redraw or thicken the stair edges. Do not alter the number or placement of steps. Do not add any vertical joint, crack, decoration, broad color gradient, haze or blur to cover the defect. Do not retouch the entire scene. The existing stair structure is already aligned; only the small unnatural hard color-block seam needs repair. All far surroundings must remain unchanged.
No text, watermark, guide marks or border. Preserve the full original image extent.'''
 (out/'prompt.txt').write_text(prompt,encoding='utf-8')
 params={'tool':'image_gen.imagegen','mode':'built-in-edit','transparent_background':False,'referenced_image_paths':[str(out/'guide-native.png')],'requestedSize':[1254,1254],'baseFile':str(BASE),'baseHash':EXPECTED,'contextTileBox':box,'contextWorldBox':[v+12288 for v in box],'defectTileBox':defect,'defectContextBox':d,'guideFile':str(out/'guide-native.png'),'guideHash':hashlib.sha256((out/'guide-native.png').read_bytes()).hexdigest(),'promptFile':str(out/'prompt.txt')}
 (out/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(params,ensure_ascii=False))
