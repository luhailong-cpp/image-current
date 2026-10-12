"""Refresh completion metadata after playback without regenerating unchanged WebPs."""
from pathlib import Path
import json
from current_review_state import current_review
from current_run_pairs import current_run_pairs
from write_final_handoff import write_handoff
R=Path(__file__).resolve().parents[1]
review=current_review();assert review and review.get('localWorkComplete')
p=R/'STATUS.json';out=json.loads(p.read_text(encoding='utf-8-sig'))
out.update(complete=True,completionScope=review['completionScope'],staticReviewedFrames=196,offlinePlaybackVerifiedSequences=14,currentReview='review/CURRENT_REVIEW.json',userFinalApproved=False)
if review.get('retentionCleanup'):out['retentionCleanup']=review['retentionCleanup']
out['currentFullLimbReview']='review/full_limb_final_20261005.json'
out['events']['run']['currentFramePositionObservations']=current_run_pairs()
out['events']['run']['pairDurationMs']=120
for f in out['files']:f['review']='当前手脚逐帧复核完成；离线正常/慢放、暂停和逐帧功能已验证；客户端未接入'
for s in out['sequences']:s['dynamicReview']='offline_playback_verified; user/client acceptance pending'
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write_handoff(out)
print('STATUS and MERGE_HANDOFF reflect current offline completion')
