import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
Z=Path(__file__).resolve().parents[1];N=Z/'native'
stem=sys.argv[1]
assert stem.startswith('r08_c05_repair_')
receipt=N/(stem+'.receipt.json'); req=N/(stem+'.request.json');target=N/(stem+'.png')
r=json.loads(receipt.read_text(encoding='utf-8-sig'));q=json.loads(req.read_text(encoding='utf-8-sig'))
assert not target.exists()
shutil.copy2(r['sourcePath'],target)
im=Image.open(target);assert im.size==(1254,1254),(im.size,stem)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec={'file':target.as_posix(),'sha256':sha(target),'generatedAt':r['finishedAtUtc'],'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'modelEvidence':'Actual model and quality not returned by builtin entry point.','role':'local_native_repair','status':'candidate_pending_visual_and_composition','nativePixelsResampled':False,'submittedParameters':q['submittedParameters'],'coordinates':q['coordinates'],'prompt':q['prompt'],'references':[{'path':p,'sha256':sha(p)} for p in q['submittedParameters']['referenced_image_paths']],'evidence':{'receipt':receipt.as_posix(),'request':req.as_posix()}}
out=N/(stem+'.png.generation.json');assert not out.exists();out.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':target.as_posix(),'sha256':rec['sha256'],'size':im.size}))
