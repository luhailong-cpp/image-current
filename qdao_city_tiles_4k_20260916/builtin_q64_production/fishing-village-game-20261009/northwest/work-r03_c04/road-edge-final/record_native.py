from pathlib import Path
import json,sys,hashlib,shutil
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
id=sys.argv[1];req=read(W/(id+'.request.json'));rec=read(W/(id+'.receipt.json'))
dst=W/(id+'.png')
if not dst.exists():shutil.copy2(rec['originalFile'],dst)
im=Image.open(dst);assert im.size==(1254,1254)
cfg=B.parents[3]/'config/image-generation.json'
meta={'file':str(dst),'sha256':sha(dst),'generatedAt':rec['returnedAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(cfg),'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in tool has no model/quality selectors or response metadata. Config is target only.','evidence':{'receipt':str(W/(id+'.receipt.json')),'request':str(W/(id+'.request.json')),'fields':['output_hint']},'prompt':req['promptFile'],'references':[{'file':p,'sha256':s,'role':r} for p,s,r in zip(req['referenced_image_paths'],req['referenceHashes'],req['referenceRoles'])],'globalCoreBox':req['globalCoreBox'],'globalNativeBox':req['globalNativeBox'],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'status':'candidate-pending-final-seam-review'}
(W/(id+'.png.generation.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(dst),'sha256':sha(dst),'dimensions':im.size}))
