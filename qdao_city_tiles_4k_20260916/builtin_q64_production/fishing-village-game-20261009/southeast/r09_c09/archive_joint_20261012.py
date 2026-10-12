from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
from PIL import Image
T=Path(__file__).resolve().parent;stem,source,response=sys.argv[1:4];R=T/'repairs';src=Path(source)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=R/f'{stem}.request.json';d=json.loads(req.read_text());prompt=R/f'{stem}.prompt.txt'
raw=T/'raw'/f'{stem}-builtin.png';out=R/f'{stem}.png'
for dest in (raw,out):
 if dest.exists():assert sha(dest)==sha(src), 'Refuse different existing output'
 else:shutil.copy2(src,dest)
im=Image.open(out);assert im.size==(1254,1254)
receipt=R/f'{stem}.receipt.json'
rec={'receivedAt':datetime.now(timezone.utc).isoformat(),'sourcePath':str(raw),'builtinSourcePath':str(src),'rawSha256':sha(raw),'nativeDimensions':list(im.size),'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'toolResponse':json.loads(Path(response).read_text())}
if not receipt.exists():receipt.write_text(json.dumps(rec,indent=2),encoding='utf-8')
record={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'nativeBoxGlobal':d.get('globalBox',d.get('nativeBoxGlobal')),'tileBox':d['tileBox'],'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'prompt':str(prompt),'promptSha256':sha(prompt),'references':[{'path':p,'sha256':sha(p),'role':d['referenceRoles'][str(i)]} for i,p in enumerate(d['referenced_image_paths'],1)],'evidence':{'request':str(req),'requestSha256':sha(req),'receipt':str(receipt),'receiptSha256':sha(receipt),'sourcePath':str(raw)},'resamplingApplied':False,'status':'native_joint_candidate_pending_adoption_QA'}
out.with_suffix('.png.generation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out),'dimensions':list(im.size)}))
