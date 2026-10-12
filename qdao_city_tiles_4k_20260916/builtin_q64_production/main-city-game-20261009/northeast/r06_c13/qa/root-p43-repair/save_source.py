from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
name,source=sys.argv[1:3]
dest=B/'source'/f'{name}.png';dest.parent.mkdir(exist_ok=True)
if not dest.exists():shutil.copy2(source,dest)
assert sha(source)==sha(dest)
r=json.loads((B/'prompts'/f'{name}.request.json').read_text(encoding='utf-8'))
with Image.open(dest) as im:w,h=im.size;fmt=im.format
d={'file':str(dest),'sha256':sha(dest),'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen','route':'builtin','nativeSize':[w,h],'width':w,'height':h,'format':fmt,'resized':False,'sourceOutputPath':source,'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host tool returned image_url/output_hint only; no actual model/quality disclosed.','prompt':str(B/'prompts'/f'{name}.prompt.txt'),'request':str(B/'prompts'/f'{name}.request.json'),'evidence':str(B/'receipts'/f'{name}.receipt.json'),'references':[{'file':p,'sha256':sha(p),'role':role} for p,role in zip(r['referenced_image_paths'],r['referenceRoles'])]}
Path(str(dest)+'.generation.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(dest),'sha256':sha(dest),'nativeSize':[w,h]}))
