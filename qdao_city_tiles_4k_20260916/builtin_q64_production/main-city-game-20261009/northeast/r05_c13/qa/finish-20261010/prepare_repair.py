from pathlib import Path
import json,hashlib
from PIL import Image
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
TILE=HERE.parents[1]; ZONE=TILE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contract=json.loads((ZONE.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
for d in ['inputs','source','records','prompts','review']: (HERE/d).mkdir(exist_ok=True)
candidate=TILE/'candidates/r05_c13.candidate.png'
assert sha(candidate)=='e56703e6af101b62306e1ff5ad4fccde7c8df2524ffd37417257a72b9b3bf746'
rid='m02-lower-v1'
box=[1700,2842,2954,4096]
target=HERE/'inputs'/f'{rid}.png'
Image.open(candidate).crop(box).save(target)
prompt='''Use case: precise-object-edit. This is a material-seam repair for an existing native-resolution isometric Daoist Q-style game map, not a new scene.
Image 1 is the exact 1254x1254 native pixel edit target. Return the same dimensions, camera, crop, and geometry. Image 2 is the approved overall layout; image 3 is the material/detail style; image 4 is the user's Daoist art style reference. Images 2-4 only constrain style, do not copy their composition or add objects.
In image 1 an artificial straight vertical color/texture step appears at x=348, most obviously across the blue-grey road slabs from y=460 to y=930. Remove this artificial generation-tile line. Repaint only stone surface material in the narrow area x=170..550, y=0..1120, matching the established pale neutral grey stone and natural muted blue-grey road. The transition should be naturally continuous and have crisp small stone brush marks, not a flat stripe, blur or airbrush. Match the intact texture/color at both sides; there must be no vertical line at x=348 or a new rectangle outline. At the top and bottom of the edited region match the intact material exactly.
Keep every existing grout line, slab corner, bevel, road border and its highlights at the exact same pixel location. Preserve all shapes and lighting. Preserve pixels outside the edited stone-surface area, including the last 134 bottom rows. No new seams, cracks, objects, text, decorations, perspective change, rescaling, stretching, noise filter or blur. Preserve the finely finished bright clean rounded game-art rendering. Output only the corrected full 1254 square image.'''
(HERE/'prompts'/f'{rid}.prompt.txt').write_text(prompt,encoding='utf-8')
refs=[str(target),contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference']]
args={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
save(HERE/'prompts'/f'{rid}.request.json',args)
save(HERE/'records'/f'{rid}.input.json',{'id':rid,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':str(candidate),'candidateSha256':sha(candidate),'nativeCrop':box,'inputDimensions':[1254,1254],'noResampling':True,'references':[{'file':p,'sha256':sha(p),'role':r} for p,r in zip(refs,['exact native edit target','layout only','near-view style','user original style'])],'configuredTarget':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'actualModel':None,'actualQuality':None})
print(HERE/'prompts'/f'{rid}.request.json')
