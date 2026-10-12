"""Record root's actual E/W sheet, native and visible browser observations."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from contact_validation import validate_contact
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat();root=read(R/'audit/bamboo-root-acceptance.json')
for d in ['E','W']:
 c=validate_contact(R,d,require_preview=False)
 preview={'reviewedAt':now,'page':'bamboo-reference.html','method':'Actual CUA browser controls and representative screenshots; full16 full-body/leg contact sheets and selected1254px native images. Not continuous video capture or hardware FPS measurement.','normal':{'cycleMs':1200,'displayPx':240,'played':True,'visibleSampleFrames':[4] if d=='E' else [5]},'quarterSpeed':{'cycleMs':4800,'displayPx':240,'played':True,'visibleSampleFrames':[9] if d=='E' else [4]},'paused480pxFrames':[15,16,1] if d=='E' else [7,8,9,16,1],'loopStep':'16→01 actual next-frame button','observations':'四个支撑位置及摆动腿推进在16帧连图可追踪；屏幕左右两半圈的腿连接有区别，后前掌踩下、前摆脚悬空后换脚。晶体始终由右手托住，左手与白狐保持连续。' + ('W08耳顶比07略高，但头脸宽度在正常240px及放大前后邻帧检查中没有明显不同身份尺度；未平移整图作补偿。' if d=='W' else 'E15/16后掌局部下压后，与01换脚关系清楚，支撑腿未外翻。'),'clientValidated':False}
 c['status']='passed_offline_four_spatial_pairs';c['rootPreview']=preview;c['reviewedAt']=now
 save(R/'audit'/f'contact-{d}-review.json',c)
 root['directions'][d]={'status':'accepted_offline_after_user_feedback','reviewedAt':now,'frames':c['frames'],'method':preview['method'],'notes':[preview['observations'],'16张独立姿态，每位置2张，实际PNG的SHA绑定本次离线审核。'],'contactReview':f'audit/contact-{d}-review.json','rootPreview':preview,'clientValidated':False}
 validate_contact(R,d)
save(R/'audit/bamboo-root-acceptance.json',root)
print('E and W actual offline preview recorded; other directions unchanged.')
