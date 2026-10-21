from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
D=T/'repairs/west-stone-joints-20261013-v1/trial-20261013T164845-W01-alpha-v2-W03'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=['step01-W01-alpha-v2/composed-core-join-1254.png','step01-W01-alpha-v2/top-boundary-100pct.png','step01-W01-alpha-v2/right-boundary-100pct.png','step01-W01-alpha-v2/bottom-boundary-100pct.png','W01-h1024-q0-after-100pct.png','step02-W03/composed-core-join-1254.png','step02-W03/top-boundary-100pct.png','step02-W03/right-boundary-100pct.png','step02-W03/bottom-boundary-100pct.png','step02-W03/protected-object-notch-100pct.png','step02-W03/fixed-west-boundary-100pct.png']
report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root independent visual inspection through view_image','candidate':str(D/'step02-W03/candidate-4096.png'),'candidateSha256':sha(D/'step02-W03/candidate-4096.png'),'scale':'1:1 crops as saved; no preview substituted','viewed':[{'path':str(D/f),'sha256':sha(D/f)} for f in files],'findings':{'W01-alpha-v2':'passed_local: join centerline and both endpoints continuous, shoulder no longer creates a hard block or extra structural line; native texture varies locally and remains observational. h1024 crossing inspected.','W03':'passed_local: repaired grout crosses fixed west core, top/right/bottom insertion perimeter has no visible geometry discontinuity; original red paper protected notch retained.','W02':'not_reviewed_or_passed_by_this_report; remains failed pending per worker record and two-attempt rule'},'scope':'Only named two repairs and saved surrounding boundaries. Does not confer whole tile external acceptance.','formalAccepted':False}
p=D/'root-independent-local-qa-20261013.json'
with p.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(p),'sha256':sha(p),'candidateSha256':report['candidateSha256']}))
