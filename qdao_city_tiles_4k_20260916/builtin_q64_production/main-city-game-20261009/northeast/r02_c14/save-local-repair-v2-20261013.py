from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;name=sys.argv[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=T/'receipts'/(name+'.receipt.json');reqpath=T/'prompts'/(name+'.request.json');rec=read(receipt);req=read(reqpath)
src=Path(rec['sourceOutputPath']);dest=T/'native/repairs'/(name+'.png');dest.parent.mkdir(exist_ok=True)
assert not dest.exists()
with Image.open(src) as im:assert im.size==(1254,1254) and im.format=='PNG'
shutil.copy2(src,dest)
target=req['repairTarget']
j={'file':str(dest),'sha256':sha(dest),'tool':'image_gen','route':'builtin','generatedAt':datetime.now(timezone.utc).isoformat(),'sourceOutputPath':str(src),'nativeSize':[1254,1254],'width':1254,'height':1254,'format':'PNG','actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool did not disclose actual model or quality.','prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(reqpath),'evidence':str(receipt),'references':[{'file':p,'sha256':sha(Path(p)),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'repairTarget':target,'baseCandidate':target['baseCandidate'],'resized':False,'status':'native_local_repair_awaiting_composed_boundary_QA'}
Path(str(dest)+'.generation.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native':str(dest),'sha256':j['sha256']}))

