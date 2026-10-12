import json,hashlib,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
source=Path(job['source']);im=Image.open(source)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'file':str(source),'sha256':sha(source),'generatedAt':job['generatedAt'],'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((ROOT.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':[x['path'] for x in job['references']]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes and returns no model/quality selectors or values.','prompt':job['prompt'],'references':[dict(x,sha256=sha(x['path'])) for x in job['references']],'evidence':{'receipt':job['receipt']},'disposition':'candidate pending comparison','visualStatus':job['visualStatus']}
Path(sys.argv[2]).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sha256':r['sha256'],'size':[im.width,im.height]}))
