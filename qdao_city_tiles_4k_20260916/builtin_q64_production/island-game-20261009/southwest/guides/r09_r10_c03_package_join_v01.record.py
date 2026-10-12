from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
stem='r09_r10_c03_package_join_v01'
src=Path('C:/Users/luyua/.codex/generated_images/01a1257c-207e-7641-9787-7abf0e2b872b/exec-18ab8b50-fea8-411d-a5e9-7353e84aece6.png')
dst=ROOT/'native'/(stem+'.png')
assert not dst.exists()
shutil.copy2(src,dst)
with Image.open(dst) as im:width,height=im.size;fmt=im.format;mode=im.mode
assert (width,height)==(1254,1254) and mode=='RGB'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
req=load(ROOT/'prompts'/(stem+'.request.json'))
rec={'file':dst.as_posix(),'sha256':sha(dst),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':width,'height':height,'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':load(Path('D:/work/image/config/image-generation.json')),'configEvidenceAtIngest':'current project config; actual host selection not disclosed','submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host has no model or quality selectors and returns no independently verified version evidence.','prompt':(ROOT/'prompts'/(stem+'.prompt.txt')).as_posix(),'references':req['references'],'sourceToolPath':src.as_posix(),'evidence':[{'path':(ROOT/'receipts'/(stem+'.tool.json')).as_posix(),'type':'successful built-in receipt; image data omitted'},{'path':(ROOT/'receipts'/(stem+'.attempt1.error.json')).as_posix(),'type':'first call failed with network error and no returned image'}],'coordinates':load(ROOT/'prompts'/(stem+'.coordinates.json')),'status':'native_repair_candidate_awaiting_two_tile_composite','nativeSizeMatchesPlan':True,'visualObservation':'The y584 horizontal leaf/rope discontinuity is removed in the displayed native result. Existing leaf wrapper silhouettes, red/beige rope paths, wood wall and paving are retained. Composite perimeter and left external edge remain pending.'}
with Path(str(dst)+'.generation.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'file':dst.as_posix(),'sha256':rec['sha256'],'dimensions':[width,height],'nativeGlobalBox':rec['coordinates']['nativeGlobalBox']}))
