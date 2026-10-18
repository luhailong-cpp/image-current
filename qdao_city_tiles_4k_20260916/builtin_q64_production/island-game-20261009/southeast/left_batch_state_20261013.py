from workflow import ROOT,read,write,sha,now
from pathlib import Path
import sys
tile,action,*args=sys.argv[1:];assert tile in ['r13_c10','r14_c10','r14_c11']
f=ROOT/f'left-batch-state-{tile}-20261013.json'
j=read(f) if f.exists() else {'tile':tile,'requests':{}}
if action=='start':
 for key in args:
  rc,v=key.split(':');pid=tile+'_p'+rc;reqfile=ROOT/'prompts'/f'{pid}_{v}.request.json';q=read(reqfile)
  assert not (ROOT/'native'/f'{pid}_{v}.png').exists()
  assert sha(Path(q['promptPath']))==q['promptSha256']
  for ref in q['references']:assert sha(Path(ref['file']))==ref['sha256']
  q.update(status='submitted_in_flight',submittedAt=now());write(reqfile,q)
  j['requests'][key]={'patch':pid,'version':v,'route':'builtin','submittedAt':q['submittedAt'],'status':'in_flight'}
else:
 key=args[0];j['requests'][key].update(status=action,updatedAt=now())
j['updatedAt']=now();write(f,j)
flight=[x for x in j['requests'].values() if x['status']=='in_flight']
for pfile in [ROOT/f'progress-{tile}.json',ROOT/f'production-resume-left-sol-{tile}-20261012.json']:
 p=read(pfile);p.update(updatedAt=now(),inFlightRequests=flight,inFlight=bool(flight),activeImageGenCalls=len(flight),inFlightRequestCount=len(flight),newGenerationAttempted=True,actualNativeCount=len(list((ROOT/'native').glob(tile+'_*.png'))),generatedNativeCount=len(list((ROOT/'native').glob(tile+'_*.png'))),status='generating' if flight else 'native_received_pending_neighbor_review');write(pfile,p)
print({'pending':len(flight),'tile':tile})
