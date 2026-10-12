from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
name=sys.argv[1];src=Path(sys.argv[2]);dst=T/'native'/(name+'.png')
if dst.exists(): raise RuntimeError('Never overwrite native')
shutil.copy2(src,dst)
im=Image.open(dst);assert im.size==(1254,1254)
payload=json.loads((T/'prompts'/(name+'.request.json')).read_text(encoding='utf8'))
config=json.loads((T/'native'/'p11.png.generation.json').read_text(encoding='utf8'))['configSnapshot']
data={'file':str(dst),'sha256':sha(dst),'nativeSize':[1254,1254],'width':1254,'height':1254,'format':'PNG','dimensionsMatch1254Plan':True,'tool':'image_gen','route':'builtin','sourceOutputPath':str(src),'generatedAt':datetime.now(timezone.utc).isoformat(),'configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host disclosed no actual model or quality','resized':False,'status':sys.argv[3],'prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(T/'prompts'/(name+'.request.json')),'evidence':str(T/'receipts'/(name+'.receipt.json')),'references':[{'file':p,'sha256':sha(p),'role':payload['referenceRoles'][i]} for i,p in enumerate(payload['referenced_image_paths'])],'assetRole':'localized native seam repair candidate'}
Path(str(dst)+'.generation.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print(json.dumps({'native':str(dst),'sha256':sha(dst),'status':sys.argv[3]}))

