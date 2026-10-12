import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
p=Q/'block2x2-r10r11c06c07-v3-trace.json';t=read(p);v2=read(Q/'block2x2-r10r11c06c07-v2-trace.json');cs={a['tile']:rgb(a['context']['path']) for a in t['tiles']}
checks=[]
for a,b,axis in [('r10_c06','r10_c07','h'),('r11_c06','r11_c07','h'),('r10_c06','r11_c06','v'),('r10_c07','r11_c07','v')]:
 same=np.array_equal(cs[a][:,-230:],cs[b][:,:230]) if axis=='h' else np.array_equal(cs[a][-230:],cs[b][:230]);assert same;checks.append({'tiles':[a,b],'shared230HaloExact':True})
for row in [10,11]:
 west=Q/f'block2x2-r10r11c05c06-v1-r{row}_c05-context-native.png';assert np.array_equal(rgb(west)[:,-230:],cs[f'r{row}_c06'][:,:230]);checks.append({'tiles':[f'r{row}_c05',f'r{row}_c06'],'westNeighbor':ref(west),'shared230HaloExact':True})
views=[]
for a in t['qa']:
 result={**a,'result':'pass','review':'native-scale inspected in this run; corrected rail top and native hard-mask boundaries clean'}
 if a['edge']=='east-shared' and a.get('part') in [4,5]:
  older=next(v for v in v2['qa'] if v['edge']==a['edge'] and v.get('part')==a['part']);assert np.array_equal(rgb(a['path']),rgb(older['path']));result['review']='Reuse explicitly viewed v2 crop after exact pixel equality verification; v3 change lies beyond QA core at outer halo'
 views.append(result)
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed','scope':'r11_c07 internal and four available r10/r11 c06/c07 shared edges; future south/east outer joins pending','reviewer':'finish_c07_resume','trace':ref(p),'internalAuditReused':ref(Q/'r11_c07-internal-visual-audit-v1.json'),'nativeQaWindowsViewedV1':21,'nativeQaChangesReviewedV2':2,'nativeQaChangesReviewedV3':1,'viewed':views,'completeRepairCropViewed':{**t['repair']['after'],'result':'pass','nativeScale':True},'checks':checks,'westRebase':t['westRebases'],'actualImageModel':None,'nativeSourceSaved':t['repair']['native'],'formalAcceptedCount':0}
out=Q/'block2x2-r10r11c06c07-v3-art-audit-v1.json';assert not out.exists();out.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'audit':ref(out),'trace':ref(p),'tiles':t['tiles'],'sharedHaloChecks':len(checks)}))
