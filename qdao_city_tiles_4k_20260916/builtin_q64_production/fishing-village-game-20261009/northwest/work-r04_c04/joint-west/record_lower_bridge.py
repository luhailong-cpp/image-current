from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
D=Path(sys.argv[1]);name=sys.argv[2];R=D.parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=read(D/(name+'.request.json'));r=read(D/(name+'.receipt.json'));p=R/'native'/(name+'.png');assert not p.exists()
shutil.copy2(r['originalFile'],p);im=Image.open(p)
g={'file':str(p),'sha256':sha(p),'generatedAt':r['generatedAt'],'width':im.width,'height':im.height,'format':im.format,'tool':r['tool'],'route':'builtin','configSnapshot':q['configSnapshot'],'configEvidence':q['configEvidence'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':r['unverifiedReason'],'evidence':{'receipt':str(D/(name+'.receipt.json')),'receiptSha256':sha(D/(name+'.receipt.json')),'request':str(D/(name+'.request.json')),'requestSha256':sha(D/(name+'.request.json')),'fields':['output_hint']},'prompt':q['promptFile'],'promptSha256':sha(q['promptFile']),'references':q['references'],'globalCoreBox':q['globalCoreBox'],'globalNativeBox':q['globalNativeBox'],'nativeCoreCropBox':[115,115,1139,1139],'nativeScaleResampled':False,'status':'candidate-pending-seam-QA'}
Path(str(p)+'.generation.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert im.size==(1254,1254),'Native dimension mismatch, no resize allowed'
print(json.dumps({'file':str(p),'sha256':sha(p),'size':im.size}))

