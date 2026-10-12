import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa';pre='block2x2-r09r10c03c04-v1'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,data):
 assert not p.exists(),p
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return ref(p)
tpath=Q/(pre+'-trace.json');t=read(tpath)
p=Path(t['context']['path']);assert ref(p)['sha256']==t['context']['sha256']
im=Image.open(p);contexts=[]
for tile,x,y in [('r09_c03',0,0),('r09_c04',4096,0),('r10_c03',0,4096),('r10_c04',4096,4096)]:
 out=Q/(pre+'-'+tile+'-context-native.png');assert not out.exists()
 crop=im.crop((x,y,x+4326,y+4326));crop.save(out)
 d={'tile':tile,**ref(out),'dimensions':[4326,4326],'source':t['context'],'sourceBox':[x,y,x+4326,y+4326],'globalContextBox':[8077+x,32653+y,8077+x+4326,32653+y+4326],'operation':'integer crop only','nativePixelsResampled':False}
 save(Path(str(out)+'.derivation.json'),d);contexts.append(d)
for q in t['qa']:assert ref(Path(q['path']))['sha256']==q['sha256']
rightOld=np.array(Image.open(t['sources']['southeast']['path']).convert('RGB'))
rightNew=np.array(Image.open(contexts[3]['path']).convert('RGB'))
eastHaloUnchanged=np.array_equal(rightOld[:,-230:],rightNew[:,-230:])
assert eastHaloUnchanged
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_rebuild','status':'native_art_join_visual_pass','trace':ref(tpath),'context':t['context'],'nativeQaCount':21,'viewed':[{'path':q['path'],'sha256':q['sha256'],'edge':q['edge'],'result':'pass'} for q in t['qa']],'findings':['All four shared edges, five original-size crops each, plus central 900px junction viewed.','Tree bark, foliage, red canopy, railing, paving, lamp, wall face and sand are continuous across joins.','No blocking seam or geometry defect found. No repair generation necessary.'],'mechanical':{'sourcePixelIdentity':t['sourcePixelIdentity'],'hardSourceChoice':True,'noResize':True,'r10c04East230PixelsUnchanged':eastHaloUnchanged},'formalAcceptedCount':0}
ar=save(Q/(pre+'-art-audit.json'),audit)
handoff={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r10_c03','status':'native_art_candidate_handoff_to_root_for_canonical','nativePatches':16,'internalQa':ref(Q/'r10_c03-internal-native-art-audit-v1.json'),'joinAudit':ar,'trace':ref(tpath),'context':t['context'],'contexts':contexts,'candidates':t['tiles'],'nextTile':'r11_c03','pending':'Root canonical export and index update only; no requested art repairs outstanding.','gitWrites':False,'frozenReceiptPreserved':ref(Q/'stair_rebuild-migration-freeze-20261011.json'),'actualModel':None,'actualQuality':None}
hr=save(Q/'r10_c03-final-art-handoff-v1.json',handoff)
print(json.dumps({'handoff':hr,'audit':ar,'contexts':[{'tile':c['tile'],'path':c['path'],'sha256':c['sha256']} for c in contexts]}))

