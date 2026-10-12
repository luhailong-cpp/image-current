from pathlib import Path
import json,datetime,hashlib
B=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
reports={n:{'path':str(B/n),'sha256':hashlib.sha256((B/n).read_bytes()).hexdigest()} for n in ['capacity-gate-review.json','capacity-gate-provenance-review.json','capacity-gate-reference-availability.json']}
qa=read(B/'capacity-gate-review.json');p=read(B/'progress.json');assert qa['sources']['candidate']['sha256']==p['candidateSha256']
p.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='capacity_layout_gate_active_review_complete',capacityGateReviewComplete=True,capacityGateReports=reports)
write(B/'progress.json',p)
ack=read(B/'capacity-gate-ack.json');ack.update(readOnlyReviewComplete=True,reviewReports=reports,internalWorkerCurrentStatus='read-only review completed; no new image requests or coordinate generation',inFlightStatus={'imageGen':'none','pendingNativeResults':0,'startedNewImageCallsThisResumption':0,'note':'Gate received before any new image generation; review only completed.'})
write(B/'capacity-gate-ack.json',ack)
print(json.dumps({'status':p['status'],'reports':list(reports),'newImageCalls':0,'fullyCovered':1,'internalPassed':1,'externalPassed':0,'formalAccepted':0,'missingFullyCovered':63}))

