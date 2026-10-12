from workflow import *
from pathlib import Path
req=read(ROOT/'prompts/r09_c13_seam2_v02.raw.json')
refs=req.pop('refs')
for r in refs:r['sha256']=sha(Path(r['file']))
pf=ROOT/'prompts/r09_c13_seam2_v02.prompt.txt';pf.write_text(req['prompt'],encoding='utf-8')
write(ROOT/'prompts/r09_c13_seam2_v02.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})

