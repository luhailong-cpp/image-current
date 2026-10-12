
from production import *
U=ROOT/'r11_c05';Q=U/'rejected';n='p01_02';tag=n+'.attempt01';req=json.loads((U/'prompts'/f'{n}.request.json').read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-7dc520ff-3ec6-4c48-880d-7813dcec29c7.png')
for ext in ['prompt.txt','request.json']:shutil.copy2(U/'prompts'/f'{n}.{ext}',Q/f'{tag}.{ext}')
with Image.open(src) as im:size=list(im.size)
ev=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
write(Q/f'{tag}.png.generation.json',{'file':str(src),'sha256':sha(src),'width':size[0],'height':size[1],'generatedAt':now(),'tool':'image_gen.imagegen','configSnapshot':ev['configurationSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'prompt':str(Q/f'{tag}.prompt.txt'),'promptSha256':sha(Q/f'{tag}.prompt.txt'),'references':req['references'],'coordinates':req['coordinates'],'sourceOutputPath':str(src),'status':'rejected','reason':'Invented staggered vertical stair-stone joints including inside fixed upper overlap; not copied into workspace.','formalAccepted':False,'evidence':{'toolReceipt':str(Q/f'{tag}.receipt.json')}})
req['prompt']='''GEOMETRY OVERRIDE: Each HORIZONTAL STAIR TREAD is ONE CONTINUOUS MONOLITHIC STONE spanning across the entire image. ZERO VERTICAL GROUT LINES, ZERO segmented stone blocks, ZERO staggered brick joints, ZERO cracks. The native upper strip and left strip have NO vertical stone joints and MUST stay unchanged. Only parallel horizontal tread/riser edges are visible. NO pale vertical lines anywhere in the stair faces. The top-left tiny clipped side curb is the only vertical structure and must not be extended elsewhere. Match native left tread heights exactly. Keep stone smooth with sparse very faint brush texture only.\n\n'''+req['prompt']
(U/'prompts'/f'{n}.prompt.txt').write_text(req['prompt'],encoding='utf-8');write(U/'prompts'/f'{n}.request.json',req)
print('p01_02 no-vertical-joints retry prepared')

