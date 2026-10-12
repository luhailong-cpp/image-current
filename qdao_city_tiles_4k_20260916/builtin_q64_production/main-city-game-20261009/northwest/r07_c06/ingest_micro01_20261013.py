from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repair-batches/shared-west-micro-01';H=Path('C:/Users/luyua/.codex/generated_images/01a1345e-0afa-7220-8dcc-4eee714800d3/exec-111791ba-1aeb-4b63-8349-a0e3647e79fa.png')
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def wj(f,v):
 assert not f.exists(),str(f)
 f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert ref(H)['sha256']==ref(D/'native.png')['sha256'];im=Image.open(D/'native.png');assert im.size==(1254,1254)
wj(D/'generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceHostFile':str(H),'native':ref(D/'native.png'),'request':ref(D/'request.json'),'parameters':ref(D/'parameters.json'),'nativeWorldBox':[19853,26776,21107,28030],'tileOriginXY':[-627,2200],'route':'builtin_image_gen','actualModel':None,'actualQuality':None,'hostByteIdentical':True,'nativePixels':[1254,1254],'formalAccepted':False})
for y in [395,1090]:
 box=(592,y-35,662,y+35);im.crop(box).save(D/f'output-y{y}.png');Image.open(D/'edit-target.png').crop(box).save(D/f'input-y{y}.png')
