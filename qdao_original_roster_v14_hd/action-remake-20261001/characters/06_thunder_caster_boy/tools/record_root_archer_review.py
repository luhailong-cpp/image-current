"""Save root's actual image observations with immutable current hashes."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
A=R.parent/'09_bamboo_archer_girl'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[A/'preview/qa'/f'run-{d}-contact.png' for d in ['S','SE','NW']]
refs += [A/f'runtime/run/{d}/{n:02d}.png' for d,n in [('S',1),('SE',1),('NW',1),('NW',9)]]
refs += [A/f'runtime/hit/{d}/01.png' for d in ['E','W']]
notes={
 'run/S':'实际对照09正面16帧。两靴鞋头沿向镜头的前后轴，03/15此前外扭已修；04–07及12–15露底来自前摆抬脚，不是向左右外撇。保留16帧。左右支撑交替，右腿前时左牌手向前，左腿前时右杖手向前；白绑腿和两件持物保留。',
 'run/SE':'实际对照09东南16帧。支撑鞋头朝画面右下、脚跟靠左上；04–06/12–13前摆露底与回收靴不应误判为外八。02–03两臂经过中位，07–10右杖前左牌后，11–15左牌前右杖后；保留当前16帧。',
 'run/NW':'实际对照09西北16帧，并放大当前00/08与09 NW01。支撑靴近端为后跟：00右下靴具有明确独立金色跟块，鞋尖伸向左上；08左下靴同样鞋尖位于左上、圆形近端为后跟。后摆腿露整块鞋底合理。此前06–10反臂与12–15错腿已修，保留当前16帧；09v6头部恢复到邻帧范围。',
 'hit/E':'实际查看6张修正原生输出，近侧靴不再朝左外撇，两靴向右；受击后仰与抬脚姿态保留。对照09 E01同向鞋轴。',
 'hit/W':'实际查看6张修正原生输出。01–05v3鞋尖向左；00旧v3/v4/v5仍右向，明确拒收。最终00v6从W05正确双靴结构重新生成独立受击起势，已查看两金鞋头均位于各靴左端，脚跟右端。对照09 W01。'
}
rows=[]
for key,note in notes.items():
 action,direction=key.split('/');count=16 if action=='run' else 6
 rows.append({'sequence':key,'staticFootAxis':'reviewed_current_images','hands':'reviewed_current_images','observation':note,'frames':[{'file':f'runtime/{key}/{i:02d}.png','sha256':sha(R/f'runtime/{key}/{i:02d}.png')} for i in range(count)],'clientVerified':False})
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'basis':'最新用户指定09竹弓少女当前版本；实际看参考图片，不复制图像或机械套帧号','references':[{'path':str(p),'sha256':sha(p),'role':'foot-axis and run arm/grounding visual reference only'} for p in refs],'sequences':rows,'normalRunTiming':{'frameMs':75,'cycleMs':1200,'source':'latest explicit user request'},'limitations':['离线逐帧美术观察不等同客户端位移接地验收','完整正常与慢速页面播放证据另见all_sequence_playback报告']}
(R/'review/root_archer_comparison_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sequences':len(rows),'framesReviewed':sum(len(x['frames']) for x in rows)}))
