import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(name,d):
 p=Q/name;assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return ref(p)
p=Q/'full-tile-r11_c03-assembly.json';a=json.loads(p.read_text(encoding='utf-8-sig'))
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c03','status':'internal_native_art_pass_north_join_pending','reviewer':'stair_rebuild','assembly':ref(p),'context':a['context'],'output':a['output'],'nativePatchCount':16,'nativeQaCount':39,'viewed':[{'file':x['file'],'sha256':x['sha256'],'result':'pass'} for x in a['qa']],'findings':['Viewed all 15 vertical, 15 horizontal and 9 intersection crops at original size.','Sand texture, boulder contours, grass boundary, stone post/rails, wooden tub and pot have no blocking seam.','Whole tile composition was viewed separately for layout only.'],'formalAcceptedCount':0,'limits':['North join still pending. Future east join delegated to root when r11_c04 is made.']}
ar=save('r11_c03-internal-native-art-audit-v1.json',audit)
m={'outputPrefix':'pair-r10c03-r11c03-v1','inputs':[{'tile':'r10_c03','context':ref(Q/'block2x2-r09r10c03c04-v1-r10_c03-context-native.png')},{'tile':'r11_c03','context':a['context']}],'provenance':[ref(Q/'block2x2-r09r10c03c04-v1-trace.json'),ref(p),ar],'repairTargets':[]}
mr=save('r11c03-northjoin-manifest-v1.json',m)
print(json.dumps({'audit':ar,'manifest':mr}))

