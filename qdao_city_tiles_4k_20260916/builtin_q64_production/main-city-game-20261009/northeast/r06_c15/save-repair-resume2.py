from pathlib import Path
import json,hashlib,shutil,sys
from PIL import Image
T=Path(__file__).resolve().parent
name=sys.argv[1]
req=T/'prompts'/f'{name}.request.json'
rp=T/'receipts'/f'{name}.receipt.json'
r=json.loads(rp.read_text(encoding='utf-8'))
src=Path(r['sourceOutputPath'])
dest=T/'native/repairs'/f'{name}.png'
dest.parent.mkdir(exist_ok=True)
assert not dest.exists()
shutil.copy2(src,dest)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(dest)
assert im.size==(1254,1254)
record={'tool':'image_gen','route':'builtin','sourceOutputPath':str(src),'native':str(dest),'sha256':sha(dest),'sourceByteIdentical':sha(dest)==sha(src),'nativeSize':list(im.size),'request':str(req),'requestSha256':sha(req),'receipt':str(rp),'receiptSha256':sha(rp),'actualModel':None,'actualQuality':None}
Path(str(dest)+'.generation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
