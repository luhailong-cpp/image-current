from pathlib import Path
from PIL import Image
import sys,shutil
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R));import production as p
stem,source=sys.argv[1:3];src=Path(source);dst=R/'native'/(stem+'.png');assert not dst.exists();shutil.copy2(src,dst)
im=Image.open(dst);assert im.size==(1254,1254) and im.mode=='RGB'
req=p.load(R/'prompts'/(stem+'.request.json'))
for ref in req['references']:assert p.hashfile(ref['path'])==ref['sha256']
rec={'file':dst.as_posix(),'sha256':p.hashfile(dst),'generatedAt':p.now(),'width':1254,'height':1254,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':p.CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool exposes neither model/quality selectors nor identity.','prompt':(R/'prompts'/(stem+'.prompt.txt')).as_posix(),'references':req['references'],'sourceToolPath':src.as_posix(),'evidence':[{'path':(R/'receipts'/(stem+'.tool.json')).as_posix(),'type':'tool receipt; image data omitted'}],'coordinates':req['coordinates'],'status':'awaiting_visual_QA','nativeSizeMatchesPlan':True}
p.dump(str(dst)+'.generation.json',rec)
idx=R/'qa/r10_c04-right-column-worker-map.json';d=p.load(idx);d['generationCount']+=1;d['updatedAtUtc']=p.now();p.dump(idx,d)
print({'stem':stem,'sha256':rec['sha256']})
