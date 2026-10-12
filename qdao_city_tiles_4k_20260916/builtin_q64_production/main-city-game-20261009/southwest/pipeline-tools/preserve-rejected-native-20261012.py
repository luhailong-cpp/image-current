import json,sys,shutil,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent
tile,patch,attempt,src,receipt,request=sys.argv[1:]
source=Path(src); folder=B/tile/'refinement/versions'/attempt
folder.mkdir(parents=True,exist_ok=True)
target=folder/(patch+'.rejected-native.png'); assert not target.exists(), target
shutil.copy2(source,target)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(target); im.load()
d={'file':str(target),'sha256':sha(target),'sourceOutputPath':str(source),'pixels':list(im.size),'nativePixelsPreserved':True,'resizedAfterGeneration':False,'receipt':receipt,'receiptSha256':sha(receipt),'request':request,'requestSha256':sha(request),'selected':False,'explicitlyRejected':True,'formalAccepted':False,'savedAtUtc':datetime.now(timezone.utc).isoformat()}
assert d['sha256']==sha(source)
(folder/(patch+'.preservation.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
