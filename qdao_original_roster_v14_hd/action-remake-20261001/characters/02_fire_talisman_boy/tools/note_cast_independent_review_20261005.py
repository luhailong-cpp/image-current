from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
paths=['frames/cast/E/02.png','frames/cast/E/03.png','work/grounding-v2/north/E/full-limb-cast-E04-20261005-a02.png','frames/cast/E/05.png','frames/cast/E/06.png']
d={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','method':'Five full-canvas images actually viewed with view_image; no resized bounding-box comparison.', 'frames':[{'path':p,'sha256':hashlib.sha256((R/p).read_bytes()).hexdigest()} for p in paths],'observations':'E04 a02右掌夹持五张符扇，左拳从对应袖口握单铃，铃垂腰侧。04到05为从腰侧低位抬铃，扇臂抬高蓄势；03到04同时伴随躯干转向，位移较大而非均匀摆臂。脚掌接地与屈膝保持。未以二维等距作为施法动作硬约束。','decision':'a02可作为E04的腰侧低位中间姿态，最终正式导入和动态抽样由后续当前SHA记录确认。','clientIntegrated':False}
(R/'reviews/full-limb-cast-E04-independent-root-20261005.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print({'actualFullImageViews':len(paths),'candidate':'E04-a02'})
