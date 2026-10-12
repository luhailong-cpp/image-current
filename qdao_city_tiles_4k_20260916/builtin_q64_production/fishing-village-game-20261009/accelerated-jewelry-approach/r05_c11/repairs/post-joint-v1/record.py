from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
p=D/'native-result.png';req=read(D/'request.json');receipt=read(D/'receipt.json');im=Image.open(p)
assert im.size==(1254,1254)
data={'file':str(p),'sha256':sha(p),'nativeDimensions':list(im.size),'format':im.format,'nativePixelsResized':False,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None,'unknownReason':'Built-in tool does not expose verified actual model/quality metadata','sourcePath':receipt['originalFile'],'sourceSha256':sha(receipt['originalFile']),'prompt':req['prompt'],'promptFile':str(D/'prompt.txt'),'promptSha256':sha(D/'prompt.txt'),'requestFile':str(D/'request.json'),'requestSha256':sha(D/'request.json'),'receiptFile':str(D/'receipt.json'),'receiptSha256':sha(D/'receipt.json'),'references':[{'file':f,'sha256':sha(f),'role':req['referenceRoles'][i]} for i,f in enumerate(req['referenced_image_paths'])],'receipt':receipt,'targetDerivationFile':str(D/'target.derivation.json'),'targetDerivationSha256':sha(D/'target.derivation.json'),'tileBox':[1400,-115,2654,1139],'status':'proposal_pending_native_compositing_and_QA','formalAccepted':False,'recordedAt':datetime.now(timezone.utc).isoformat()}
(D/'native-result.generation.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'nativeDimensions':list(im.size),'sha256':sha(p)}))
