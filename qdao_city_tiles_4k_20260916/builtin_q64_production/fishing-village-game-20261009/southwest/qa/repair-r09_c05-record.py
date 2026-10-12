import json,hashlib,sys
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parents[1]
stem=sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=z/'native'/f'{stem}.png'
req=json.loads((z/'native'/f'{stem}.request.json').read_text(encoding='utf-8-sig'))
receiptpath=z/'native'/f'{stem}.receipt.json'
receipt=json.loads(receiptpath.read_text(encoding='utf-8-sig'))
assert receipt['result']['output_hint']
for r in req['references']: assert sha(r['path'])==r['sha256']
im=Image.open(p); assert im.size==(1254,1254)
record={'file':p.as_posix(),'sha256':sha(p),'generatedAt':receipt['finishedAtUtc'],'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads((z.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in image tool exposes no model or quality selector and returned no verified model or quality metadata. Config is target only.','evidence':{'receipt':receiptpath.as_posix(),'receiptFields':['result.output_hint'],'pngMetadataKeys':list(im.info.keys())},'prompt':(z/'native'/f'{stem}.prompt.txt').as_posix(),'promptSha256':sha(z/'native'/f'{stem}.prompt.txt'),'request':{'path':(z/'native'/f'{stem}.request.json').as_posix(),'sha256':sha(z/'native'/f'{stem}.request.json')},'references':req['references'],'coordinates':req['coordinates'],'repairBounds':req['repairBounds'],'margin':req['margin'],'status':'candidate_pending_local_mask_qa','nativePixelsResampled':False}
Path(str(p)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':p.as_posix(),'sha256':sha(p),'dimensions':im.size}))

