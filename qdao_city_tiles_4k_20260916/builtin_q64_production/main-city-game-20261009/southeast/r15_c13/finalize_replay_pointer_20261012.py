from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent
def r(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def w(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def info(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
p=T/'candidate/r15_c13-resume-v2-20261012-manifest.json';m=r(p);m['replayScript']=info(T/'replay_resume_v2_20261012.py');w(p,m);mi=info(p)
for name in ['candidate/latest-assembly.json','candidate/selection-20261012.json']:
 p=T/name;o=r(p);o['manifest']=mi;w(p,o)
p=T/'production-resume-20261012.json';o=r(p);o['selection']['manifest']=mi;o['manifest']=mi;o['replayScript']=info(T/'replay_resume_v2_20261012.py');w(p,o)
for name in ['handoff-r15_c13-20261012.json','local-continuation-20261012.json']:
 p=T/name;o=r(p);o['currentSelection']['manifest']=mi;o['resumeRecord']=info(T/'production-resume-20261012.json');o['replayScript']=info(T/'replay_resume_v2_20261012.py');w(p,o)
print(json.dumps({'manifest':mi,'replayScript':info(T/'replay_resume_v2_20261012.py'),'handoff':info(T/'handoff-r15_c13-20261012.json')},indent=2))
