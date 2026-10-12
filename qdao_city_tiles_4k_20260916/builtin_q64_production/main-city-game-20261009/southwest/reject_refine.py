
from production import *
R=T/'refinement'
Q=R/'rejected'
Q.mkdir(exist_ok=True)
n='p04_04';tag=n+'.attempt01'
req=json.loads((R/'prompts'/f'{n}.request.json').read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-13050471-418e-4c8a-b9d1-fb8a57514c07.png')
for ext in ['prompt.txt','request.json']:
    shutil.copy2(R/'prompts'/f'{n}.{ext}',Q/f'{tag}.{ext}')
with Image.open(src) as im:size=list(im.size)
e=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
rec={'file':str(src),'sha256':sha(src),'width':size[0],'height':size[1],'generatedAt':now(),'tool':'image_gen.imagegen','configSnapshot':e['configurationSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'prompt':str(Q/f'{tag}.prompt.txt'),'promptSha256':sha(Q/f'{tag}.prompt.txt'),'references':req['references'],'coordinates':req['coordinates'],'editedFrom':req['editSource'],'sourceOutputPath':str(src),'status':'rejected','reason':'Wrong image edited: returned whole-city composition instead of the native stair crop. Not copied into the southwest workspace.','formalAccepted':False,'evidence':{'toolReceipt':str(Q/f'{tag}.receipt.json')}}
write(Q/f'{tag}.png.generation.json',rec)
extra='CRITICAL TARGET CHECK: Image1 is ONLY a VERY CLOSE CROP of SIX HORIZONTAL STONE STAIR TREADS, filling the entire square. The output MUST still show ONLY these six cropped horizontal stairs, nothing else. No buildings, no city, no courtyard, no complete staircase scene. Do not output image2 (the whole-city style reference). Keep exactly the first image camera/crop/six tread boundaries. The requested change is simply reduce the surface texture on these stairs.\n\n'
req['prompt']=extra+req['prompt']
(R/'prompts'/f'{n}.prompt.txt').write_text(req['prompt'],encoding='utf-8')
write(R/'prompts'/f'{n}.request.json',req)
print(json.dumps({'rejectedRecord':str(Q/f'{tag}.png.generation.json'),'retryPrepared':True}))

