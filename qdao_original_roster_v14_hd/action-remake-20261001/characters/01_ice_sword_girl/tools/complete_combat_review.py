"""Attach actual static review without altering PNGs; keep all record SHA links current."""
import json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
action,direction=sys.argv[1:3]
assert action in ['hit','attack','cast'] and direction in ['E','W']
report=R/f'review/combat-{action}-{direction}-review.json';v=read(report)
sp=R/f'review/combat-{action}-{direction}-selection.json';s=read(sp)
s['events']=v.get('events',{});s['artStatus']=v['status'];s['reviewRecord']=report.relative_to(R).as_posix()
for i,f in enumerate(s['frames']):
 phase=v['actualPhaseByFrame'][i]
 obs={'status':'actual_static_sequence_review','actualPhase':phase,'reviewRecord':report.relative_to(R).as_posix(),'method':v['reviewMethod'],'clientRuntimeVerified':False,'formalAcceptance':False}
 gp=R/f['sourceGenerationRecord'];g=read(gp)
 rp=R/g['evidence']['receipt'];receipt=read(rp);receipt['visualReview']=obs;write(rp,receipt)
 g['evidence']['receiptSha256']=sha(rp);g['visualReview']=obs;write(gp,g)
 dp=R/f['generationRecord'];dg=read(dp);dg['derivedFrom']['generationRecordSha256']=sha(gp);dg['visualReview']=obs;write(dp,dg)
 f['actualPhase']=phase;f['actualContact']=v.get('actualContactByFrame',[None]*len(s['frames']))[i]
 f['notes']='Actual static review: '+phase+'. '+ ' '.join(v.get('remaining',[]))
write(sp,s)
print(json.dumps({'selection':str(sp),'reviewAttached':len(s['frames']),'pngsUnchanged':True}))
