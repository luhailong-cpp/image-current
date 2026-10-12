from pathlib import Path
import json, hashlib, sys
from PIL import Image

root=Path(__file__).resolve().parents[1]
n=int(sys.argv[1]); key=f'{n:02}'
image_path=root/f'.work/cast/W/{key}.png'
receipt=root/f'records/cast/W/{key}.receipt.json'
data=json.loads(receipt.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((root/'MODEL_VERIFICATION.json').read_text(encoding='utf-8'))['configSnapshot']
refs=[('D:/work/image/designs/pets-xianling-20260924/source/16-luhualing-E.png','native E identity'),('D:/work/image/designs/pets-xianling-20260924/source/16-luhualing-W.png','native W identity and rear anatomy'),('D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','primary style/material reference')]
with Image.open(image_path) as im:
    meta={'file':f'runtime/cast/W/{key}.png','sourceFile':image_path.relative_to(root).as_posix(),'sourceSha256':sha(image_path),'generatedAt':data['returnedAt'],'startedAt':data['startedAt'],'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'action':'cast','direction':'W','frame':n,'durationMs':45,'pivot':[0.5,0.08],'event':'release' if n==11 else None,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[p for p,r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际型号和质量；无参数选择器。','prompt':f'prompts/cast/W/{key}.txt','references':[{'path':p,'role':r,'sha256':sha(Path(p))} for p,r in refs],'evidence':{'receipt':receipt.relative_to(root).as_posix(),'imagePayload':'Native PNG from tool-returned path; exact SHA stored.'},'technical':{'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'alphaBBox':im.getchannel('A').getbbox() if im.mode=='RGBA' else None},'visualStatus':'pending','exportStatus':'pending root unified export'}
if 'request' in data:
    meta['submittedParameters'].update(data['request'])
    meta['references']=data.get('references',meta['references'])
    meta['prompt']=data.get('promptPath',meta['prompt'])
    if data.get('editTarget'): meta['editTarget']=data['editTarget']
(root/f'records/cast/W/{key}.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frame':key,'width':meta['width'],'height':meta['height'],'sha256':meta['sourceSha256']}))
