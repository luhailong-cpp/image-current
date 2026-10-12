"""Record root's actual image observations for this round, separately from automated playback."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
notes={
'runtime/cast/W/14.png':'近侧左靴恢复朝西长侧面，踝点与屈膝保留；与新13和15衔接，双手握持未变。',
'runtime/cast/W/15.png':'近侧鞋尖朝左，侧面与右后跟对应W方向，收势双臂和另一靴保持。',
'runtime/run/SE/02.png':'左牌回到自身左肩连接的画面右腰侧，避免01到04中跨躯干跳位；下身保持。',
'runtime/run/SE/03.png':'同相位独立前后摆姿态，牌手肩肘相接，腿鞋与相机保持。',
'runtime/run/NE/02.png':'实看v3原生：近侧右支撑靴窄后跟与后缝可见，鞋尖沿NE远离相机；不再前开。',
'runtime/run/NE/03.png':'实看v2原生：去除近侧支撑靴朝相机大鞋头/前底，踝与窄后跟连贯。',
'runtime/run/W/02.png':'左牌从前方收到腰侧，右杖屈肘由后伸收至远侧腰部，作为01到03中间姿态。',
'runtime/run/W/09.png':'近左牌从后方收至腰旁、右杖后收，08到10之间通过肩肘真实中段，不交换持物。',
'runtime/run/E/14.png':'右杖肩肘继续13到15后伸相位，消除单帧突然收臂；左牌与下身保持。',
'runtime/run/NW/09.png':'左牌由上端倒握修为下沿握持，牌顶上伸，不再08到10间单帧倒转。',
'runtime/run/SE/06.png':'保留：鞋底投影偏水平，但髋膝踝与踝至鞋头向右下推进，前靴呈SE三分之四透视；不能仅以鞋底边角度判外翻。',
'runtime/run/SE/07.png':'保留：与06同向独立初接/缓冲，膝踝鞋头连通，未见独立反折或横向分腿。'}
frames=[{'file':p,'sha256':sha(R/p),'actualVisualObservation':n} for p,n in notes.items()]
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'root','method':'实际显示原生/正式单帧与相邻帧，非仅元数据检查','frames':frames,'timing':{'frameMs':60,'cycleMs':960},'isFinalAll196Review':False,'clientIntegrated':False}
(R/'review/root_full_limb_observations_20261005.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('root observations recorded: '+str(len(frames)))

