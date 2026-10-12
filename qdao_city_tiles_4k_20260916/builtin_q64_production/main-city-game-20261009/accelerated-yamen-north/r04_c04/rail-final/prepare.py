from pathlib import Path
from PIL import Image
import json,hashlib

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
PROJECT=ROOT.parent.parent
NORTH=ROOT/'qa-repair-native/exported-native-v1/s04_01-internal4-derived.png'
SOUTH=PROJECT/'northwest/r05_c04/native/s01_01.png'
BEST=ROOT/'repair-s04_01/fix08/generated.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p,box):return {'file':str(p),'sha256':sha(p),'worldBox':box,'dimensions':list(Image.open(p).size)}
n=Image.open(NORTH).convert('RGB');s=Image.open(SOUTH).convert('RGB')
assert n.size==s.size==(1254,1254)
context=Image.new('RGB',(1254,1254))
context.paste(n.crop((0,512,1254,1024)),(0,0))
context.paste(s.crop((0,0,1254,742)),(0,512))
context.save(OUT/'anchored-context-native.png')
context.crop((600,260,1110,770)).save(OUT/'before-rail-detail-native.png')
spec={'contextWorldBox':[12173,15757,13427,17011],'formalSouthBoundaryContextY':627,'realSouthStartsContextY':512,'sources':[info(NORTH,[12173,15245,13427,16499]),info(SOUTH,[12173,16269,13427,17523]),info(BEST,[12173,15245,13427,16499])],'construction':'Top context rows 0..511 = north native rows 512..1023. Bottom context rows 512..1253 = unmodified true south rows 0..741. All same-world-coordinate copying; no resize/warp/blend in guide.'}
(OUT/'preparation.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
prompt='''Use case: precise-object-edit. Edit image 1 at its exact native 1254 x 1254 dimensions and framing. It is a piece of hand-painted pale stone balustrade beside stairs and a green architectural relief.
Repair the ONE connection of the long cream stone rail across the visible horizontal mismatch near image y=512. The upper rail is too wide toward the right. Reconstruct the north/upper run of the rail, approximately x=640..1080 and y=100..540, so that it naturally tapers down and meets the immutable lower rail. Smoothly connect EVERY individual longitudinal line: the left dark recess, gray side plane, bright beveled edge, inner left groove, wide cream face, inner right groove, and outer right edge. Continue the lower rail's exact edges upward and reconcile them gradually with the exact upper endpoints. The lower half is already finished; do not solve the mismatch by moving, widening, narrowing or repainting it. Preserve all pixels below y=570 as closely as possible. The top 100 rows are fixed upper endpoints. Changes to the upper rail may extend through the intervening length; avoid a short bend, zigzag or sudden step.
Image 2 is the older northern 1254px patch, a secondary geometry reference ONLY: its lower right rail edge is already close to the real lower rail. Image 1 is the sole composition and exact crop target. Do not copy image 2's framing. The same world coordinate in image 2 is y(image1)+512.
Preserve the exact surrounding stone blocks, green plaque, staircase tread positions and painted material scale. No new bands, collars, horizontal joints, ornaments, scars, blur, haze, artificial shadow or decorative object to conceal the join. The result must look like one uninterrupted original stone rail at full native detail. No text, border, watermark, resizing, reframing or camera changes. Output exactly 1254x1254 pixels.'''
(OUT/'prompt-v1.txt').write_text(prompt,encoding='utf-8')
args={'prompt':prompt,'referenced_image_paths':[str(OUT/'anchored-context-native.png'),str(BEST)],'transparent_background':False}
(OUT/'parameters-v1.json').write_text(json.dumps(args,indent=2),encoding='utf-8')
print(json.dumps(spec))
