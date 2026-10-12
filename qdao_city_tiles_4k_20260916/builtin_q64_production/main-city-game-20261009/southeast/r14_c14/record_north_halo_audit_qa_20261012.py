from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;D=T/'repairs/north-halo-audit-20261012'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':str(p),'sha256':sha(p)}
def put(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
now=datetime.now(timezone.utc).isoformat();proof=rd(D/'provenance.json');results=[]
for mode in ['linear24','linear40','minerror8to96','linear24-partial']:
 d=D/mode;m=rd(d/'composition.json')
 for a in [m['baseCandidate'],m['baseContext'],m['sourceHalo'],m['alpha'],m['candidate'],m['context'],m['compositor'],m['nativeProvenance']]:assert sha(a['path'])==a['sha256']
 for a in [proof['selectedNeighbor'],proof['selectedNeighborContext']]:assert sha(a['path'])==a['sha256']
 base=np.array(Image.open(m['baseCandidate']['path']).convert('RGB'));alpha=np.array(Image.open(m['alpha']['path']));halo=np.array(Image.open(m['sourceHalo']['path']).convert('RGB'));replay=base.copy();a=alpha[:,:,None].astype(np.uint32)
 replay[:115]=((halo.astype(np.uint32)*a+base[:115].astype(np.uint32)*(255-a)+127)//255).astype(np.uint8)
 actual=np.array(Image.open(m['candidate']['path']).convert('RGB'));assert np.array_equal(actual,replay) and actual.shape==(4096,4096,3)
 context=np.array(Image.open(m['baseContext']['path']).convert('RGB'));context[115:4211,115:4211]=replay;assert np.array_equal(context,Image.open(m['context']['path']).convert('RGB')) and context.shape==(4326,4326,3)
 frozen=np.array(Image.open(T/'candidate/r14_c14-4k-candidate-8ff54f4e9ec7de483b1a.png').convert('RGB'))[:630,:630];assert np.array_equal(actual[:630,:630],frozen)
 assert np.array_equal(actual[115:],base[115:]) and np.array_equal(actual[:115][alpha==0],base[:115][alpha==0])
 partial=mode=='linear24-partial'
 view={'reviewedAt':now,'reviewer':'assembly_support','status':'local_pass_partial_trial' if partial else 'local_fail','candidateSha256':m['candidate']['sha256'],'mechanicalReplay':True,'sourceProvenance':'Every halo pixel replays from four original1254 natives and recorded row4 alpha; all receipt/request/prompt/reference/original hashes checked.','sourceStructuralQA':'All four original1254 native images viewed in full. Source south strips continue their own stone/wood/shadow without an intrinsic core/halo boundary break. This is source-only approval; joining into the child needs separate QA.','resized':False,'rgbCorrectionPerformed':False,'frozenCornerUnchanged':True,'northCoreUnchanged':True,'formalAccepted':False,'published':False}
 if partial:
  view.update(scope={'changedBounds':[630,0,2874,24],'fullyAppliedAtNorthBoundaryX':[662,2842],'leftFadeX':[630,662],'rightFadeX':[2842,2874]},viewed=['joined-x630-1254.png','joined-x1600-1254.png','join-endpoint-x630-100pct.png','join-endpoint-x1024-100pct.png','join-endpoint-x1490-100pct.png','join-endpoint-x2048-100pct.png','join-endpoint-x2842-100pct.png','join-endpoint-x2874-100pct.png'],findings=['Grey paving, grout and wood grain become continuous at the fixed north boundary in the changed range.','No new clearly broken edge, double contour or transition hard line was observed in the applied partial range.','Stone crossing at x1490 and the two internal vertical seam entries x1024/x2048 were inspected; structure remains connected.','The right fade lies within a broad existing wood post, before the rejected far-east ledge/shadow region.','All pixels y24 onward and x2874 onward are unchanged. Existing full internal QA outside the24px top edge is retained.'],remaining=['Frozen NW630 region remains root-owned.','Far-east x2874..4096 still has the original north structure/shadow mismatch and is excluded from this partial trial.','This local assessment does not pass the entire external edge or formally accept the tile.'])
 elif mode in ['linear24','linear40']:
  view.update(viewed=['joined-x630-1254.png','joined-x1600-1254.png','joined-x2842-1254.png','left-bevel-detail-100pct.png','shadow-detail-100pct.png'],findings=['Narrow native continuity removes the exact fixed-y0 material line.','At far-east ledge the genuine north geometry and the child geometry do not agree. The alpha transition bends/smears the left bevel around corex3050..3200,y0..40.','The broad shadow terminates/fades rapidly along the narrow horizontal transition around corex3500..4000,y0..40, instead of continuing consistently over the stepped wood.'],decision='Reject as a whole-edge repair. Source provenance is valid but the entire applied geometry is not.')
 else:
  view.update(viewed=['seam-x630-100pct.png','seam-x1600-100pct.png','seam-x2842-100pct.png','left-bevel-detail-100pct.png','shadow-detail-100pct.png'],findings=['Minimum-error paths searchy8..96 and span that full range.','Several wood grain/tone changes follow a visibly jagged cut.','The large far-east shadow has an obvious staircase cutoff and the left ledge remains incompatible.'],decision='Reject wide minimum-error whole-edge repair.')
 put(d/'visual-review.json',view)
 results.append({'mode':mode,'candidate':m['candidate'],'manifest':art(d/'composition.json'),'visualReview':art(d/'visual-review.json'),'mechanicalReplay':True,'status':view['status']})
cur=rd(T/'candidate/latest-assembly.json');assert cur['candidate']['sha256']==proof['baseChild']['sha256'];assert rd(T/'repairs/latest-repair.json')['candidate']['sha256']==cur['candidate']['sha256']
summary={'recordedAt':now,'tile':'r14_c14','provenance':art(D/'provenance.json'),'auditScript':art(T/'audit_north_halo_20261012.py'),'allOriginalSourcesAndReceiptsVerified':True,'allSelectedHaloPixelsExactlyReplayed':True,'nativeCoreHaloContinuityForX630Onward':True,'sourceNativeVisualQA':'four full1254 natives viewed; south-strip source structures coherent','trials':results,'viability':'Partial narrow24px native extension is usable for local improvement through x2874. No tested halo-only method passes the far-east ledge/shadow.','latestPublishedCandidate':cur['candidate'],'latestPointerUnchanged':True,'activeNativeCount':16,'historicalNativeCount':36,'newGenerationCount':0,'workerNetworkCalls':0,'oldFailedBuiltinTrialsPreserved':True,'frozenCornerUnchanged':True,'formalAccepted':False,'requiredNext':'Root may independently review partial10d492d6. Far-east structure needs a localized native repair anchored to this proved north continuation and the child interior; do not deepen the halo blend to hide it.'}
put(D/'audit-and-trial-report.json',summary)
r=rd(T/'production-resume-20261012.json');r.update(updatedAt=now,northHaloAuditAndTrials=art(D/'audit-and-trial-report.json'),nextStep=summary['requiredNext']);(T/'production-resume-20261012.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
p=rd(T/'progress.json');p.update(updatedAt=now,northHaloAudit=str(D/'audit-and-trial-report.json'),nextStep=summary['requiredNext'],pendingOfflineTrial='north-halo-linear24-partial-trial-20261012',pendingOfflineTrialStatus='local_pass_partial_unpublished');(T/'progress.json').write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'report':art(D/'audit-and-trial-report.json'),'selectedPartialTrial':results[-1],'latestPublished':cur['candidate'],'formalAccepted':False},indent=2))

