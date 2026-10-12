from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent;d=T/'repairs/north-shadow-narrow-composed-v1-20261012';v=T/'repairs/north-shadow-narrow-20261012T142136-02d97dd1'
def rd(p):return json.loads(p.read_text(encoding='utf-8'))
def art(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
m=rd(d/'composition.json');g=rd(v/'generation.json');a=rd(T/'candidate/latest-assembly.json');b=rd(T/'repairs/latest-repair.json')
assert a['candidate']['sha256']==b['candidate']['sha256']=='66848fcdb5ff648de5f448588dbb4cd1c70693dee07ea43f3b15da0ed353d377'
now=datetime.now(timezone.utc).isoformat();count=len(list((T/'native').glob('*.generation.json')))+len(list((T/'repairs').glob('*/generation.json')));repairs=len(list((T/'repairs').glob('*/generation.json')))
assert count==36 and repairs==18
out={'recordedAt':now,'version':v.name,'sourceNative':g['native'],'original':g['originalOutput'],'receipt':g['receipt'],'generation':art(v/'generation.json'),'trialCandidate':m['candidate'],'trialManifest':art(d/'composition.json'),'visualReview':art(d/'visual-review.json'),'mechanicalReplay':{'replayed':True,'reservedCornerUnchanged':True,'outsideSavedMaskUnchanged':True,'neighborCoreUnchanged':True},'status':'failed_not_published','publishedCandidate':a['candidate'],'historicalNativeCount':count,'activeNativeCount':16,'actualModel':None,'actualQuality':None,'formalAccepted':False,'workerNetworkCalls':0}
put(d/'outcome.json',out)
p=rd(T/'progress.json');p.update(updatedAt=now,status='native_external_repair_partial_pending_full_external_review',generatedNativeCount=count,historicalNativeRepairCount=repairs,pendingRepairStatus='generated_composed_visual_failed',lastRepairTrial=d.name,lastRepairTrialStatus='failed_not_published',lastRepairTrialQA=str(d/'visual-review.json'),nextStep='North narrow trial remains failed at fixed y640 and left bevel lower mask edge. Root can inspect saved failure bands and coordinate the next targeted native repair. Published west668 remains latest. Worker remains offline.',inFlightImageGenCount=0)
put(T/'progress.json',p)
r=rd(T/'production-resume-20261012.json');r.update(updatedAt=now,status=p['status'],historicalNativeCount=count,nativeRepairCount=repairs,latestNarrowNorthOutcome=art(d/'outcome.json'),pendingNarrowNorthRequestStatus='generated_composed_visual_failed',nextStep=p['nextStep'],passedButUnmergedCount=0)
r.setdefault('offlineWorkCompleted',[]).append('Byte-copied root narrow source67cbd047 native1254, mechanically composed/replayed trial209f2655 at presaved alpha, inspected upper/lower boundaries at native scale and retained failed trial without publishing.')
put(T/'production-resume-20261012.json',r)
print(json.dumps(out,indent=2))

