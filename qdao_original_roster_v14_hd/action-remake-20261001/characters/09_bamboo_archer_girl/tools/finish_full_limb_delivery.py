from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
status=read(ROOT/'status.json'); c=status['counts']
for key in ['exportedRuntimeSlots','technicalChecksPassed','nativeResolutionEvidencePassed','sourceEvidencePassed']:assert c[key]==196,key
assert c['missingSlots']==0 and not status['exactVisibleDuplicates'] and not status['exactMirroredPairs'] and not status['inventoryIssues']
review=read(ROOT/'review.json')
assert len(review['frames'])==196 and not review['staleReviews']
for row in review['frames']:assert row['sha256']==sha(ROOT/'runtime'/(row['slot']+'.png'))
preview=read(ROOT/'audit/preview-delivery-check.json')
assert preview['currentSourceReferences']==196 and preview['sourceHashMatches']
p=ROOT/'audit/full-limb-current-closeout.json';d=read(p)
assert len(d['changedFrames'])==6 and d['retainedFrames']==190
for row in d['frames']:assert row['sha256']==sha(ROOT/row['file'])
d['postRepairReviews']=[{'file':rel,'sha256':sha(ROOT/rel)} for rel in ['audit/full-limb-root-repair-review.json','audit/NW15-empty-arm-repair.json','audit/full-limb-W04-repair.json','audit/full-limb-W14-before-after-review.json','audit/full-limb-SE08-before-after-review.json']]
d['offlineVerification']={'atUtc':now,'technicalChecksPassed':196,'currentSourceReferences':196,'staleReviews':0,'normalAndSlowAnimationsVerified':28,'pairSheetsVerified':8,'dynamicVisualAcceptance':False}
write(p,d)
p=ROOT/'audit/latest-grounding-requirement.json';requirement=read(p)
requirement['latestFullLimbRevision']={'file':'audit/full-limb-current-closeout.json','correctedFrames':6,'retainedFrames':190,'reviewedRuntimeFrames':196,'offlineChecksPassed':True,'dynamicVisualAcceptance':False}
write(p,requirement)
timing=read(ROOT/'animation-timing.json')['run']
write(ROOT/'audit/live-work-state.json',{'updatedAtUtc':now,'character':'09_bamboo_archer_girl','state':'full_limb_asset_revision_delivered_offline_checks_passed','writeBoundary':'This character directory only; no Git/client/other-character writes','correctedSlots':[r['slot'] for r in d['changedFrames']],'runtimeFrames':196,'runTiming':timing,'timingClarification':{'question':'用户询问不是已改60ms/帧吗；文件实际75ms/帧，已询问最终60或75，尚未收到选择。','state':'awaiting_direct_user_answer_no_timing_change'},'delivery':'MERGE_HANDOFF.md','currentReview':'audit/full-limb-current-closeout.json','dynamicVisualAcceptance':False,'clientIntegrated':False,'remainingLimits':['Real-time browser playback and engine grounding/displacement were not verified','E/W/NW hip roots have occlusion; no unsupported anatomical same-foot tracking approval']})
print('Full-limb corrections and offline delivery verified; real-time/client remain unverified.')
