from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
case,source=sys.argv[1:];dest=HERE/'source'/f'{case}.png';assert not dest.exists();shutil.copy2(source,dest)
with Image.open(dest) as im:assert im.size==(1254,1254) and im.format=='PNG'
assert sha(source)==sha(dest)
rec=read(HERE/'records'/f'{case}.input.json');req=read(HERE/'prompts'/f'{case}.request.json');receipt=read(HERE/'receipts'/f'{case}.receipt.json')
assert (HERE/'prompts'/f'{case}.prompt.txt').read_text(encoding='utf-8')==req['prompt']
for ref in rec['references']:assert sha(ref['file'])==ref['sha256']
out={'file':str(dest),'sha256':sha(dest),'generatedAt':receipt['finishedAt'],'nativeSize':[1254,1254],'width':1254,'height':1254,'format':'PNG','resized':False,'sourceOutputPath':source,'sourceOutputByteIdentical':True,'tool':'image_gen','route':'builtin','configTargetSnapshot':read(Path('D:/work/image/config/image-generation.json')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed image_gen exposes no model or quality metadata.','prompt':str(HERE/'prompts'/f'{case}.prompt.txt'),'request':str(HERE/'prompts'/f'{case}.request.json'),'receipt':str(HERE/'receipts'/f'{case}.receipt.json'),'references':rec['references'],'input':rec,'status':'native-repair-awaiting-integration-review'}
(HERE/'records'/f'{case}.generation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'case':case,'file':str(dest),'sha256':sha(dest)}))
