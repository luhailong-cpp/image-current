from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def art(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
latest=read(T/'candidate/latest-assembly.json')
west=T/'repairs/west-material-composed-v1-20261012'
north=T/'repairs/north-platform-composed-v1-20261012'
wm=read(west/'composition.json');nm=read(north/'composition.json')
assert latest['candidate']['sha256']==wm['candidate']['sha256']
assert read(T/'repairs/latest-repair.json')['candidate']['sha256']==wm['candidate']['sha256']
records=list((T/'native').glob('*.generation.json'))+list((T/'repairs').glob('*/generation.json'))
assert len(records)==35
outcomes={'recordedAt':now,'publishedCandidate':wm['candidate'],'publishedContext':wm['context'],'publishedManifest':art(west/'composition.json'),'west':{'status':'local_material_improvement_published_full_edge_pending','review':art(west/'visual-review.json'),'qaEvidence':art(west/'qa-evidence.json')},'north':{'status':'failed_not_published','trialCandidate':nm['candidate'],'manifest':art(north/'composition.json'),'review':art(north/'visual-review.json'),'fixedSeamEvidence':art(north/'review-fixed-seam-100pct.png'),'bottomAlphaEvidence':art(north/'review-bottom-alpha-100pct.png')},'activeNativeCount':16,'historicalNativeCount':len(records),'nativeRepairCount':len(list((T/'repairs').glob('*/generation.json'))),'formalAccepted':False,'internalQA':'Previous I01-I07 pass retained; no full internal re-review this round.','externalQA':'not_passed','frozenCornerUnchanged':True,'workerNewNetworkCalls':0,'actualModel':None,'actualQuality':None}
put(T/'review/resume-offline-20261012/root-output-outcomes.json',outcomes)
r=read(T/'production-resume-20261012.json')
r.update(updatedAt=now,nativeRepairCount=outcomes['nativeRepairCount'],mechanicalMergePerformed=True,mechanicalMergeReason='Root-delivered west native was composed using stored alpha v2, reviewed and published. North native was composed and replayed but failed visual QA; retained as an unpublished trial.',rootDeliveredOutcomes=art(T/'review/resume-offline-20261012/root-output-outcomes.json'),currentReplay={'replayed':True,'candidateSha256':wm['candidate']['sha256'],'reservedCornerUnchanged':True,'outsideSavedMaskUnchanged':True,'neighborCoreUnchanged':True,'rgbCorrectionPerformed':False},freezeMatchingScope='Initial restoration baseline bfcb8104 matched the immutable freeze. Current west-material candidate is a later version; historical freeze remains unchanged.',freezeMatchesCurrentPublishedCandidate=False,nextStep='Offline handoff to root: north trial needs native continuation at fixed y640 and lower y1005..1020; remaining west material segments and frozen root corner still require separate work. Do not publish north trial as passed.',workerGeneratedNewArtworkThisRound=False,rootNewNativeOutputsReceivedThisRound=2)
r['westRemaining']['majorYStatus']='Improved and locally published; minor residual material transition remains, not full external approval.'
r['westRemaining']['latestLocalReview']=art(west/'visual-review.json')
r['northTrial']=outcomes['north']
r['offlineWorkCompleted'] += ['Byte-copied and verified both root builtin1254 originals; saved source/receipt/generation hashes with actual model and quality null.','Composed and exactly replayed both sources at saved integer crops and alpha v2; preserved frozen corner and fixed neighbor cores.','Published locally improved west candidate66848fcd and retained failed north trial1c82695d.']
r['offlineAvailableNext']=['Replay published west version or inspect saved north failure bands.','Prepare new north source target preserving immutable upper boundary and lower support continuity, for root builtin generation; this worker must remain offline.','Coordinate remaining west material segments and root-owned frozen NW corner.']
r['artWorkStillRequired']=['Resolve remaining west material transitions including moderate y1660..1820 and y3480..3760.','Correct north groove/wood/grain/ledge-shadow discontinuities, including failed trial boundary y640 and lower mask join y1005..1020.','Root-coordinated frozen NW corner and final external acceptance.']
put(T/'production-resume-20261012.json',r)
p=read(T/'progress.json')
p.update(updatedAt=now,nextStep=r['nextStep'],lastRepairTrial='north-platform-composed-v1-20261012',lastRepairTrialStatus='failed_not_published',lastRepairTrialQA=str(north/'visual-review.json'),historicalNativeRepairCount=outcomes['nativeRepairCount'],rootDeliveredOutcomes=str(T/'review/resume-offline-20261012/root-output-outcomes.json'))
put(T/'progress.json',p)
print(json.dumps(outcomes,indent=2))

