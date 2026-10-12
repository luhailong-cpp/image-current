from pathlib import Path
import json,sys,os
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
pid,ver,note=sys.argv[1:4]
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
e=rd(Q/f'{pid}-{ver}-evidence.json');e.update({'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'candidate_geometry_pass_with_material_notes','reviewer':'coordinate_audit','nativeViewed':True,'allListedEvidenceDirectlyViewed':True,'findings':note,'formalAccepted':False,'usableExternalAccepted':False});wr(Q/f'{pid}-{ver}-review.json',e)
f=R/'selected-native-r08_c11.json';d=rd(f) if f.exists() else {'tile':'r08_c11','selected':{},'formalAccepted':False};d['selected'][pid]=Path(e['native']).name;wr(f,d)
p=R/'progress-r08_c11.json';d=rd(p);d.update({'status':'patch_reviewed_continue','selectedNativeCount':len(rd(f)['selected']),'inFlight':False,'lastReview':str(Q/f'{pid}-{ver}-review.json'),'updatedAt':e['reviewedAt']});wr(p,d)
