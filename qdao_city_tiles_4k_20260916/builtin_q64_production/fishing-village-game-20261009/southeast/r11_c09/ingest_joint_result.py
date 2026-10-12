import json,hashlib,shutil,sys
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
stem,source=sys.argv[1:3];req=read(R/(stem+'.request.json'));receipt=read(R/(stem+'.receipt.json'))
dst=R/'native'/(stem+'.png');shutil.copy2(source,dst)
assert Image.open(dst).size==(1254,1254)
config=read(R/'native/p44-v1.png.generation.json')['configSnapshot']
g={'file':str(dst),'sha256':sha(dst),'nativeDimensions':[1254,1254],'tool':'image_gen__imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin exposes no selectors or returned model/quality metadata','generatedAt':receipt['receivedAt'],'ingestedAt':datetime.now(timezone.utc).isoformat(),'prompt':str(R/(stem+'.prompt.txt')),'promptSha256':sha(R/(stem+'.prompt.txt')),'references':[{'path':p,'sha256':sha(p),'role':req['referenceRoles'][str(i+1)]} for i,p in enumerate(req['referenced_image_paths'])],'evidence':{'request':str(R/(stem+'.request.json')),'requestSha256':sha(R/(stem+'.request.json')),'receipt':str(R/(stem+'.receipt.json')),'receiptSha256':sha(R/(stem+'.receipt.json')),'sourcePath':source},'coordinate':req['coordinate'],'upsamplingApplied':False,'status':'local_joint_repair_candidate_not_selected'}
dst.with_suffix('.png.generation.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dst),'sha256':sha(dst),'nativeDimensions':[1254,1254]}))

