from pathlib import Path
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1]
p=R/'review/CURRENT_REVIEW.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
archive=R/'records/review_before_full_limb_feedback_20261005.json'
if not archive.exists():archive.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
reason='用户补充全腿轴线与上肢检查：髋-膝-踝-鞋头同运动平面，肩肘腕与握持连续；保持196帧/跑步75ms'
d.update(localWorkComplete=False,reopenedAt=datetime.now(timezone.utc).isoformat(),reopenedReason=reason)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'STATUS.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s.update(complete=False,currentFullLimbReview='in_progress',reopenedReason=reason);p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'MERGE_HANDOFF.md';s=p.read_text(encoding='utf-8').replace('本机素材制作与复核已完成。','当前按2026-10-05补充要求继续复核全腿轴线、肩肘手腕与握持。本轮进行中；下方记录为已落盘素材。');p.write_text(s,encoding='utf-8')
print('Full-limb review reopened; no PNG changed by this script')
