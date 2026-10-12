import json,hashlib,uuid
from pathlib import Path
from datetime import datetime,timezone
import root_north_20261012 as n
Z=Path(__file__).resolve().parent
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):
 return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
d=json.loads((Z/'records/r04_c12.working-selection.json').read_text(encoding='utf-8-sig'))
save(Z/'records/r04_c12.partial-anchor-selection-root-v1.json',{'tile':'r04_c12','status':'partial anchors only, not complete tile','formalAccepted':False,'patches':{k:ref(Z/'native'/v) for k,v in d.items()}})
save(Z/'qa/r04_c12_p43-v3.deferred-review-20261013.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'unpassed_deferred_after_repeated_repair','versionsPreserved':[ref(Z/'native'/f'r04_c12_p43-v{i}.png') for i in range(1,4)],'observations':{'v1':'Upper blue crest lost and lower ivory ridge raised at left seam','v2':'Same geometry discontinuity; no improvement','v3':'Left and bottom seams improved but unexpected extra third blue ridge band, no selection'},'selection':None,'v4':'Guide prepared only, not submitted','nextAction':'Continue independent missing coordinates; do not propagate this unpassed geometry','formalAccepted':False})
n.init('r03_c12')
n.prep('r03_c12_p41',Z/'records/r04_c12.partial-anchor-selection-root-v1.json')
n.context('r03_c12')

