from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys,shutil
W=Path(__file__).resolve().parent;B=W.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
id=sys.argv[1];q=read(W/'receipts'/(id+'.request.json'));r=read(W/'receipts'/(id+'.receipt.json'));p=B/'native'/(id+'.png')
if p.exists():assert sha(p)==sha(r['originalFile'])
else:shutil.copy2(r['originalFile'],p)
im=Image.open(p);assert im.size==(1254,1254)
g={'file':str(p),'sha256':sha(p),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':{'route':'builtin','tool':'image_gen.imagegen','model':None,'quality':None},'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':r['unverifiedReason'],'evidence':{'receipt':str(W/'receipts'/(id+'.receipt.json')),'request':str(W/'receipts'/(id+'.request.json')),'fields':['output_hint']},'prompt':q['promptFile'],'references':[{'file':f,'sha256':sha(f),'role':q['referenceRoles'][i]} for i,f in enumerate(q['referenced_image_paths'])],'globalNativeBox':q['globalNativeBox'],'nativeScaleResampled':False,'status':'candidate-repair-pending-QA'}
Path(str(p)+'.generation.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(p),'sha256':sha(p)}))
