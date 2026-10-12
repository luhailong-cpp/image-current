from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
status=read(ROOT/'status.json')
assert status['counts']['exportedRuntimeSlots']==196
assert status['counts']['missingSlots']==0
assert not status['exactVisibleDuplicates'] and not status['exactMirroredPairs']
assert status['counts']['technicalChecksPassed']==196
assert status['counts']['nativeResolutionEvidencePassed']==196
assert status['counts']['sourceEvidencePassed']==196
assert not status['inventoryIssues']
review=read(ROOT/'review.json')
assert len(review['frames'])==196 and not review['staleReviews']
for row in review['frames']:assert row['sha256']==sha(ROOT/'runtime'/(row['slot']+'.png'))
preview=read(ROOT/'audit/preview-delivery-check.json')
assert preview['currentSourceReferences']==196 and preview['sourceHashMatches']
p=ROOT/'audit/video-axis-current-closeout.json';d=read(p)
d['postRepairReviews']=[{'file':rel,'sha256':sha(ROOT/rel)} for rel in ['audit/video-axis-root-repair-review.json','audit/N12-video-axis-repair.json','audit/video-axis-W07-before-after-review.json','audit/run-SW-03-11-video-axis-repair-review.json']]
d['offlineVerification']={'atUtc':now,'technicalChecksPassed':196,'currentSourceReferences':196,'staleReviews':0,'normalAndSlowAnimationsVerified':28,'pairSheetsVerified':8,'dynamicVisualAcceptance':False}
d['inspectionImageRetention']='Extracted video contact sheets were used for inspection and removed after final runtime/previews verified; original external video untouched and SHA/frame-crop metadata retained.'
write(p,d)
p=ROOT/'audit/video-reference-20261004/extraction.json';d=read(p)
d['inspectionImageRetention']={'status':'removed_after_review_and_final_preview_verification','ledger':'audit/cleanup-superseded-inspection-images.json','originalExternalVideoModified':False}
write(p,d)
p=ROOT/'audit/latest-grounding-requirement.json';d=read(p)
d['latestVideoAxisRevision']={'file':'audit/video-axis-current-closeout.json','correctedFrames':5,'retainedFrames':191,'offlineChecksPassed':True,'dynamicVisualAcceptance':False}
write(p,d)
write(ROOT/'audit/live-work-state.json',{'updatedAtUtc':now,'character':'09_bamboo_archer_girl','state':'video_axis_asset_revision_delivered_offline_checks_passed','writeBoundary':'This character directory only; no Git/client/other-character writes','correctedSlots':['run/N/12','run/SW/03','run/SW/11','run/SW/12','run/W/07'],'runtimeFrames':196,'runTiming':{'frames':16,'frameMs':75,'cycleMs':1200,'framesPerPosition':2},'delivery':'MERGE_HANDOFF.md','currentReview':'audit/video-axis-current-closeout.json','dynamicVisualAcceptance':False,'clientIntegrated':False,'remainingLimits':['Real-time browser playback and engine grounding/displacement were not verified','E/W hip roots remain occluded; no unsupported anatomical same-foot tracking approval']})
print('Video revision verification and delivery state recorded; dynamic/client acceptance remains unverified.')
