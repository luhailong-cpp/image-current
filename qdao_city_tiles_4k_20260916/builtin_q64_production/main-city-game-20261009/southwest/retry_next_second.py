
from production import *
U=ROOT/'r11_c05';Q=U/'rejected';n='p01_01';tag=n+'.attempt02'
req=json.loads((U/'prompts'/f'{n}.request.json').read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-8a28d9e2-38df-477c-857c-b9b94b2b491b.png')
for ext in ['prompt.txt','request.json']:shutil.copy2(U/'prompts'/f'{n}.{ext}',Q/f'{tag}.{ext}')
with Image.open(src) as im:size=list(im.size)
ev=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
write(Q/f'{tag}.png.generation.json',{'file':str(src),'sha256':sha(src),'width':size[0],'height':size[1],'generatedAt':now(),'tool':'image_gen.imagegen','configSnapshot':ev['configurationSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'prompt':str(Q/f'{tag}.prompt.txt'),'promptSha256':sha(Q/f'{tag}.prompt.txt'),'references':req['references'],'coordinates':req['coordinates'],'sourceOutputPath':str(src),'status':'rejected','reason':'Copied upper native reference full scene rather than target downward continuation; top230 leaf/curb overlap not preserved. Not copied into workspace.','formalAccepted':False,'evidence':{'toolReceipt':str(Q/f'{tag}.receipt.json')}})
req['references']=req['references'][:4];req['referenced_image_paths']=req['referenced_image_paths'][:4]
base=json.loads((Q/'p01_01.attempt01.request.json').read_text(encoding='utf-8-sig'))['prompt']
prefix='''MANDATORY IMAGE1 FRAMING: This is an EXTREME MACRO close crop, NOT a scene. Preserve the TOP230 PIXELS exactly: dense GREEN LEAVES occupy the UPPER LEFT, a huge pale stone parapet runs through top center/right, and only the narrow RIGHTMOST strip contains clipped stair tread ends. The green leaves MUST stay at the TOP LEFT, do not replace them with bare wall or move them downward.
Continue BELOW this top native strip. Follow the coarse lower target shapes: a very close vertical RED painted/banner fragment occupies x100..330 down the LEFT, cropped by bottom; a massive pale vertical stair-side stone/curb fills x550..925 through the entire height, slightly leaning left downwards, its close block base reaching the BOTTOM; only the RIGHTMOST quarter shows tightly clipped HORIZONTAL step tread ends. Do not show the whole staircase. Keep everything clipped. Do not add a symmetric entrance, complete rail, pathway, building, courtyard or arena. You are painting roughly a hand-sized detail blown up, not an overview. ONLY paint image1's coarse interior into native detail while absolutely keeping its exact crop and top strip.\n\n'''
req['prompt']=prefix+base
(U/'prompts'/f'{n}.prompt.txt').write_text(req['prompt'],encoding='utf-8');write(U/'prompts'/f'{n}.request.json',req)
print('r11_c05 retry attempt03 ready')

