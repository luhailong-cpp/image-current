
from production import *
U=ROOT/'r11_c05';Q=U/'rejected';Q.mkdir(exist_ok=True);n='p01_01';tag=n+'.attempt01'
req=json.loads((U/'prompts'/f'{n}.request.json').read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-824d6253-93b8-4ec1-960a-5ab37b2ffb7a.png')
for ext in ['prompt.txt','request.json']:shutil.copy2(U/'prompts'/f'{n}.{ext}',Q/f'{tag}.{ext}')
with Image.open(src) as im:size=list(im.size)
ev=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
write(Q/f'{tag}.png.generation.json',{'file':str(src),'sha256':sha(src),'width':size[0],'height':size[1],'generatedAt':now(),'tool':'image_gen.imagegen','configSnapshot':ev['configurationSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'prompt':str(Q/f'{tag}.prompt.txt'),'promptSha256':sha(Q/f'{tag}.prompt.txt'),'references':req['references'],'coordinates':req['coordinates'],'sourceOutputPath':str(src),'status':'rejected','reason':'Zoomed out to complete arena entrance, instead of exact macro curb crop; not copied into workspace.','formalAccepted':False,'evidence':{'toolReceipt':str(Q/f'{tag}.receipt.json')}})
prev=T/'refinement'/'native'/'p04_01.png'
req['references'].append({'file':str(prev),'sha256':sha(prev),'role':'immediately-above native patch at exactly the target scale, image5'})
req['referenced_image_paths'].append(str(prev))
prefix='''CRITICAL SCALE AND TARGET OVERRIDE. Image1 is an EXTREME MACRO close crop of ONE SINGLE GIANT PALE STONE STAIR-SIDE PARAPET. It fills the central 35% of the canvas vertically, runs through both TOP and BOTTOM edges, and is clipped. Only a NARROW RIGHTMOST STRIP (about15% width) shows clipped horizontal stair tread ends; NEVER show a complete staircase or a symmetric entrance. The LEFT side shows clipped nearby green leaves, a large red vertical banner/column fragment, and close stone shadow. There are NO complete buildings, railings, doorways, roads, courtyards, cloud motifs or arena disk visible in this tiny crop.
Image5 is the native patch directly ABOVE image1 at the identical very close scale. Image1 top230px copies image5 bottom230px. Extend this same extremely enlarged curb, leaves and clipped stair ends DOWNWARD, while following image1 coarse shapes in the new lower area. The result must look like an adjacent macro texture/object fragment, not a scene. If you render an entire stair flight or arena entrance, the output is wrong. Do not bring anything from the overall city image into this close crop.\n\n'''
req['prompt']=prefix+req['prompt']
(U/'prompts'/f'{n}.prompt.txt').write_text(req['prompt'],encoding='utf-8');write(U/'prompts'/f'{n}.request.json',req)
print('r11_c05 p01_01 macro retry prepared')

