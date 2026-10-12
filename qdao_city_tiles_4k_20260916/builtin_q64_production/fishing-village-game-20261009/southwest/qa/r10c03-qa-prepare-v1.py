import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent
Q=Z/'qa'
def ref(p): return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(name,data):
 p=Q/name
 assert not p.exists(),p
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return ref(p)
p=Q/'full-tile-r10_c03-assembly.json'
a=json.loads(p.read_text(encoding='utf-8-sig'))
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_rebuild','status':'internal_native_visual_pass_external_pending','assembly':ref(p),'context':a['context'],'output':a['output'],'nativePatchCount':16,'viewedNativeQaCount':39,'viewed':[{'file':x['file'],'sha256':x['sha256'],'result':'pass'} for x in a['qa']],'findings':['All 15 vertical, 15 horizontal and 9 intersection native crops were viewed at original size.','Wood rails, post edges, foliage, pale stone courses, wall foot and sandy ground remain continuous; no visible blocking seam.','Whole composition viewed for geometry only; no enlarged layout pixels used in final art.'],'limits':['External north/east joins and central 2x2 junction require separate QA.'],'formalAcceptedCount':0}
ar=save('r10_c03-internal-native-art-audit-v1.json',audit)
m={'outputPrefix':'block2x2-r09r10c03c04-v1','topJoint':ref(Q/'pair-r09c03-c04-v1-context-native.png'),'southwest':a['context'],'southeast':ref(Q/'block2x2-r09r10c04c05-v1-r10_c04-context-native.png'),'provenance':[ref(Q/'pair-r09c03-c04-v1-trace.json'),ref(Q/'block2x2-r09r10c04c05-v1-trace.json'),ref(p),ar],'globalContextBox':[8077,32653,16499,41075],'tiles':['r09_c03','r09_c04','r10_c03','r10_c04']}
mr=save('r10c03-block2x2-manifest-v1.json',m)
print(json.dumps({'audit':ar,'manifest':mr}))

