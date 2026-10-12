from pathlib import Path
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1]
p=R/'review/CURRENT_REVIEW.json';data=json.loads(p.read_text(encoding='utf-8-sig'))
(R/'records/review_before_video_axis_feedback_20261004.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
reason='用户新视频反馈：其他方向腿脚歪/外翻，需继续核对膝踝鞋长轴与连续扭转；原离线技术通过不代表本轮脚轴修复通过'
data.update(localWorkComplete=False,reopenedAt=datetime.now(timezone.utc).isoformat(),reopenedReason=reason)
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'STATUS.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s.update(complete=False,reopenedReason=reason,currentVideoAxisReview='in_progress');p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'MERGE_HANDOFF.md';s=p.read_text(encoding='utf-8').replace('本机素材制作与复核已完成。','当前按用户新视频反馈继续修腿脚轴线；本轮尚未完成。下方为此前已落盘资料，不代表本轮修复通过。');p.write_text(s,encoding='utf-8')
print('Reopened current visual review; all196 runtime PNGs preserved')
