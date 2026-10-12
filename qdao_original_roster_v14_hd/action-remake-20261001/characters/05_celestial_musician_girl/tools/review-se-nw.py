from pathlib import Path
import json,sys,datetime
root=Path(__file__).resolve().parent.parent
p=root/sys.argv[1]
d=json.loads(p.read_text(encoding='utf-8'))
d['visualReview']={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'actual generated image viewed at native aspect; no pixel alterations','verdict':sys.argv[2],'observations':sys.argv[3],'edgeCaveat':'Viewer color fringing may be low alpha 1-4; composite review required before rejection.'}
d['status']='candidate_needs_dynamic_review' if sys.argv[2]=='static_candidate' else 'candidate_needs_correction'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
