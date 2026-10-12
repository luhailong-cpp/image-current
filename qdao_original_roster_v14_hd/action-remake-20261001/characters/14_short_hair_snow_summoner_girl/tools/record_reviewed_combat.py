from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
p=R/'review.json'; out=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
groups=[('hit','E',6,'v11侧身修复；左右手各有袖腕连接；02至04有屈膝受击和表情变化，05至06恢复，整组靴、耳未裁切。'),('hit','W',6,'近左臂抱狐、远右掌托晶；02至04后仰/下蹲并恢复，六帧双脚和袖腕清楚。'),('attack','W',12,'蓄势03、前伸04至06、07至12收招；近左臂抱狐、远右掌托晶连续，双脚无额外肢体。')]
for a,d,count,note in groups:
 for n in range(1,count+1):
  key=f'{a}/{d}/{n:02d}'; f=R/(key+'.png')
  out[key]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'visualStatus':'passed','reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root','scope':'offline sprite anatomy, whole contact sheet, normal/quarter-speed browser playback and selected enlarged frames','notes':note,'clientValidated':False}
p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(out))

