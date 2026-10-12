from pathlib import Path
from workflow import ROOT,read,write,sha,now
import sys
tile=sys.argv[1];patches=sys.argv[2:]
flights=[]
for rc in patches:
 pid=f'{tile}_p{rc}';f=ROOT/'prompts'/f'{pid}_v01.request.json';req=read(f)
 assert not (ROOT/'native'/f'{pid}_v01.png').exists()
 if pid=='r14_c11_p11':
  pf=Path(req['promptPath']);s=pf.read_text(encoding='utf-8');s=s.replace('A tan-gray sea rock enters only from the far left edge below the upper half, following the soft layout precisely; do not enlarge or duplicate it.','The soft layout shows tan-gray rock clipped by the lower-left edge and another rock slope entering the lower-right corner, separated by a broad sea channel. Reconstruct both only at their actual layout positions without enlarging or duplicating them.');pf.write_text(s,encoding='utf-8');req['promptSha256']=sha(pf)
 req.update(status='submitted_in_flight',submittedAt=now());write(f,req);flights.append(dict(patch=pid,version='v01',route='builtin',submittedAt=req['submittedAt']))
for f in [ROOT/f'progress-{tile}.json',ROOT/f'production-resume-left-sol-{tile}-20261012.json']:
 p=read(f);p.update(updatedAt=now(),status='generating',inFlightRequests=flights,newGenerationStatus='builtin_allowed_unknown_actual_model');write(f,p)
print(flights)
