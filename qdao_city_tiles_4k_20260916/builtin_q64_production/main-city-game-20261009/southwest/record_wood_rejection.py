
from production import *
R=T/'refinement';Q=R/'rejected';n='p01_04';tag=n+'.attempt01'
req=json.loads((R/'prompts'/f'{n}.request.json').read_text(encoding='utf-8-sig'))
src=Path('C:/Users/luyua/.codex/generated_images/01a12076-0b9d-76b2-949d-c4cf520a83be/exec-e2a6af68-369e-40f1-b0ba-9f0ee5363d40.png')
for ext in ['prompt.txt','request.json']:shutil.copy2(R/'prompts'/f'{n}.{ext}',Q/f'{tag}.{ext}')
with Image.open(src) as im:size=list(im.size)
e=json.loads((ROOT/'batch-evidence.json').read_text(encoding='utf-8-sig'))
write(Q/f'{tag}.png.generation.json',{'file':str(src),'sha256':sha(src),'width':size[0],'height':size[1],'generatedAt':now(),'tool':'image_gen.imagegen','configSnapshot':e['configurationSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'prompt':str(Q/f'{tag}.prompt.txt'),'promptSha256':sha(Q/f'{tag}.prompt.txt'),'references':req['references'],'coordinates':req['coordinates'],'editedFrom':req['editSource'],'sourceOutputPath':str(src),'status':'rejected','reason':'Unintended change to grey motif silhouette at upper-left; rejected whole-patch tone repair. Not copied into workspace. Local repair crop used instead.','formalAccepted':False,'evidence':{'toolReceipt':str(Q/f'{tag}.receipt.json')}})
print('Rejected native tone-edit record saved; selected primary p01_04 unchanged.')

