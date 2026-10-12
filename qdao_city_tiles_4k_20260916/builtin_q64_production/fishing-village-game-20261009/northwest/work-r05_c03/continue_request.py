from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
W=Path(__file__).resolve().parent;B=W.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sr,sc,v=map(int,sys.argv[1:4]);id=f'r05_c03_s{sr:02d}_s{sc:02d}_v{v:02d}'
detail=Path(sys.argv[4]).read_text(encoding='utf-8')
old=read(W/'receipts/r05_c03_s02_s03_v01.request.json');prefix=old['prompt'].split('EXACT FRAGMENT:')[0]
c=read(B.parent/'production-contract.json');guide=W/'guides'/(id+'.positional.png');g=read(str(guide)+'.derivation.json')
prompt=prefix+'EXACT FRAGMENT: Global native box '+str(g['globalNativeBox'])+'. '+detail
pf=W/'prompts'/(id+'.prompt.txt');pf.write_text(prompt,encoding='utf-8')
refs=[str(guide),c['layoutReference'],c['detailStyleReference'],c['primaryStyleReference']]
q={'id':id,'createdAt':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'promptFile':str(pf),'referenced_image_paths':refs,'referenceRoles':old['referenceRoles'],'referenceHashes':[hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in refs],'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'globalNativeBox':g['globalNativeBox'],'globalCoreBox':g['globalCoreBox']}
write(W/'receipts'/(id+'.request.json'),q);print(json.dumps({'id':id,'request':str(W/'receipts'/(id+'.request.json'))}))
