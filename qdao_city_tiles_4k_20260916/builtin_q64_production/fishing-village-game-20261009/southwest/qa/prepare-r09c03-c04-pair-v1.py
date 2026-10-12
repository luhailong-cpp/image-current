import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
a=Q/'full-tile-r09_c03-assembly.json';m=json.loads(a.read_text(encoding='utf-8-sig'))
reviewed=[v for v in m['qa'] if '-v' in Path(v['file']).name or '-intersection-' in Path(v['file']).name]
assert len(reviewed)==24
audit={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r09_c03','status':'passed_vertical_and_intersection_native_qa_horizontal_review_pending','assembly':ref(a),'context':m['context'],'output':m['output'],'reviewedAtOriginalDimensions':reviewed,'reviewedCount':24,'result':'pass','notes':['15 vertical segments and 9 intersections viewed at original dimensions; no visible seams, severed paving joints, staircase fragments, foliage cutoffs or object displacement.','Whole4096 viewed scaled only for overall composition; excluded from native QA count. Doorway staircase has four continuous noses including landing edge; this is separate from r10_c04 six-step flight.'],'noGameClientTests':True,'formalAcceptedCount':0}
p=Q/'r09_c03-internal-vertical-intersection-qa-v1.json';assert not p.exists();p.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pair={'schemaVersion':1,'outputPrefix':'pair-r09c03-c04-v1','inputs':[{'tile':'r09_c03','context':ref(Q/'full-tile-r09_c03-context-native.png')},{'tile':'r09_c04','context':ref(Q/'block2x2-r09r10c04c05-v1-r09_c04-context-native.png')}],'provenance':[ref(a),ref(p),ref(Q/'block2x2-r09r10c04c05-v1-trace.json')],'repairTargets':[]}
p=Q/'pair-r09c03-c04-v1.manifest.json';assert not p.exists();p.write_text(json.dumps(pair,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(ref(p))

