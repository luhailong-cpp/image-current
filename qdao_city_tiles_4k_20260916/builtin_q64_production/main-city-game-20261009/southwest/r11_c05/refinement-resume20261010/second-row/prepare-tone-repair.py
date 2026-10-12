from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;F=D.parent;T=F.parent;R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p,role):return {'file':str(p),'sha256':sha(p),'role':role,'pixels':list(Image.open(p).size)}
source=D/'output/first-row-v5-plus-original-second-row.context.png';box=[1536,1024,2790,2278]
target=D/'inputs/row2-x2048-tone.target.png';Image.open(source).crop(box).save(target,optimize=True)
left=D/'inputs/row2-x2048-tone.left-native230.png';Image.open(target).crop((0,0,230,1254)).save(left,optimize=True)
for label,b in [('top230',[0,0,1254,230]),('bottom230',[0,1024,1254,1254])]:Image.open(target).crop(b).save(D/'inputs'/f'row2-x2048-tone.{label}.png',optimize=True)
c=json.loads((R.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
refs=[ev(target,'actual 1254x1254 native assembled edit target; exact crop, no resize'),ev(left,'exact left230 pixels of actual target; natural stone shading anchor'),ev(Path(c['layoutReference']),'approved city layout, never widen crop'),ev(Path(c['detailStyleReference']),'approved stone material/daylight'),ev(Path(c['primaryStyleReference']),'approved Daoist illustration style; never copy UI')]
prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. Return exactly one opaque native 1254 x 1254 PNG, same framing and every object in the same place.
This is a tiny material seam repair in the lower stairs of game artwork. Near the horizontal center of the image, the stone stair RISERS have an obvious irregular diagonal warm/cool polygon color boundary. Remove just that patchy color division. Continue each riser's existing natural grey shading smoothly through the center, with very gradual tonal change matching BOTH outer sides. No hard vertical, slanted or wavy tonal boundary. Image 2 is the actual left stone material for reference.
Preserve the horizontal stair grooves, tread highlights, exact edge positions, number and size of steps, shadows, rectangular ground slabs, all grout joints, and every red paper scrap EXACTLY. Do not turn the ground into stairs. Do not move, add or remove any joint or object. Do not introduce new veins, flakes or scale-like marks. Only soften the unnatural color patch boundaries on existing riser planes, retaining subtle original brush texture.
Keep the surrounding 115px perimeter and bottom230px unchanged. Keep the entire lower ground area unchanged. Do not change perspective, crop, scale or composition. The last three images are approved whole-city layout, stone materials and Daoist style only; never reproduce their scene or UI.
Final native image exactly1254x1254.'''.replace('\n+','\n')
id='row2-x2048-tone';pp=D/'prompts'/f'{id}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
req={'id':id,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptFile':str(pp),'promptSha256':sha(pp),'references':refs,'referenced_image_paths':[r['file'] for r in refs],'sourceContext':{'file':str(source),'sha256':sha(source),'cropBox':box},'cropWorldBox':[17805,41869,19059,43123],'expectedNativePixels':[1254,1254],'route':'builtin','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'status':'prepared_not_submitted'}
(D/'prompts'/f'{id}.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8');print(str(D/'prompts'/f'{id}.request.json'))
