from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
p=R/'records/full_limb_baseline_20261005.json'
assert not p.exists(),'Baseline exists; do not replace after edits'
s=json.loads((R/'STATUS.json').read_text(encoding='utf-8-sig'))
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'frames':s['files'],'runPositions':s['events']['run']['currentFramePositionObservations'],'previousPlaybackEvidence':'review/current_playback_evidence_20261004.json','previousReview':'records/review_before_full_limb_feedback_20261005.json'}
assert len(out['runPositions'])==128
p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved196 prior source rows and128 position observations')
