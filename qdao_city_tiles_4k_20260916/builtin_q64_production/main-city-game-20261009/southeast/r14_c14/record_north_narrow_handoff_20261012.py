from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent; d=T/'repairs/north-shadow-narrow-20261012T142136-02d97dd1'
def rd(p):return json.loads(p.read_text(encoding='utf-8'))
def art(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
h=rd(d/'handoff.json'); now=datetime.now(timezone.utc).isoformat()
a=rd(T/'candidate/latest-assembly.json');b=rd(T/'repairs/latest-repair.json')
assert a['candidate']['sha256']==b['candidate']['sha256']==h['currentCandidateUnchanged']['sha256']
r=rd(T/'production-resume-20261012.json')
r.update(updatedAt=now,pendingNarrowNorthRequest=art(d/'handoff.json'),nextStep='Root may generate north-shadow-narrow-20261012T142136-02d97dd1 using its saved builtin request. Worker remains offline; ingest actual original and use immutable pre-saved alpha v2, then review both upper y640 and lower y736/y880 joins before any publication.')
r.setdefault('offlineWorkCompleted',[]).append('Prepared narrow north continuation target from west668 and fixed89c0 north core, plus integer-only local crop of unadopted8516 as reference. Mask and alpha saved before returned output; no failed trial pixels selected.')
put(T/'production-resume-20261012.json',r)
p=rd(T/'progress.json');p.update(updatedAt=now,pendingRepairVersion=h['version'],pendingRepairStatus='prepared_offline_root_builtin_request',pendingRepairRequest=h['request'],nextStep=r['nextStep'],inFlightImageGenCount=0)
put(T/'progress.json',p)
print(json.dumps({'latestCandidate':a['candidate'],'pending':h['request'],'manifest':art(d/'handoff.json'),'workerNetworkCalls':0,'formalAccepted':False},indent=2))

