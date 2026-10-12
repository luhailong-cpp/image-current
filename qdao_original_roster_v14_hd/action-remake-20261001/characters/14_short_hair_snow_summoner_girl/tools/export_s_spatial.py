"""Promote visually inspected S poses; keep review pending until actual playback."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selection=read(R/'audit/root-S-spatial-selection.json');rows=[]
for ns,(slot,sourceRoot) in selection.items():
 n=int(ns);src=R/'run/staging'/f'{slot}.png';dest=R/'run/S'/f'{n:02d}.png'
 run(src,dest);rows.append({'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'srcRoot':sourceRoot,'basis':'Existing anatomical root unchanged; only local leg/boot redraw; no sole alignment or whole-character shift.'})
reg=R/'run/S/spatial-registration.json';save(reg,{'globalScale':.8,'targetRoot':[512,942],'frames':rows});apply(reg)
notes=[
 "屏幕右侧解剖左腿在前侧落脚，01较伸展、02微屈膝缓冲；屏幕左侧右腿后收，托晶手从前向中间摆。",
 "屏幕右侧左腿在髋下承重，03右腿高回收，04右膝进入抬起阶段；托晶掌继续向后摆。",
 "屏幕右侧左腿在髋后较短透视持续支撑，05右脚折后回收、06右膝带小腿前送；两个姿态各有连续的膝踝链。",
 "屏幕右侧左后脚缩短纵深并抬跟，以鞋面与向下前掌表示后侧蹬地；07/08右前鞋摆到镜头方向并露底但仍悬空，08前摆更伸。",
 "屏幕左侧解剖右腿前侧落脚，09鞋跟先前伸、10膝缓冲下压；左腿在屏幕右侧回收，晶体由右掌承托。",
 "屏幕左侧右腿经过髋下承重，11/12左膝高抬且小腿回收角度不同；左臂连续抱狐，右掌前摆托晶。",
 "屏幕左侧右脚随躯干越过进入髋后，13平掌微屈膝，14左前腿开始送出、右后腿透视更短；位置变化为纵深而非横叉。",
 "屏幕左侧右后脚抬跟前掌压地，15/16后支撑鞋面可见、前摆左鞋露底；16左脚前伸准备01落脚，两条腿连接和换脚方向清楚。"
]
now=datetime.now(timezone.utc).isoformat();pairs=[]
for i,obs in enumerate(notes):pairs.append({'frames':[2*i+1,2*i+2],'position':f'P{i%4+1}','supportLeg':'anatomical_left_screen_right' if i<4 else 'anatomical_right_screen_left','observations':obs})
frames=[{'file':f'run/S/{n:02d}.png','sha256':sha(R/'run/S'/f'{n:02d}.png')} for n in range(1,17)]
contact={'direction':'S','status':'static_pending_root_preview','reviewedAt':now,'criterion':'four_successive_positions_two_distinct_poses_each','cycleMs':1200,'durationMs':75,'frames':frames,'contacts':[{'supportLeg':'anatomical_left_screen_right','frames':list(range(1,9)),'observations':'01–08屏幕右侧左腿前落、髋下、髋后到后前掌蹬地，右腿摆动。'},{'supportLeg':'anatomical_right_screen_left','frames':list(range(9,17)),'observations':'09–16屏幕左侧右腿持续接地完成同一空间顺序，左腿摆动。'}],'positionPairs':pairs,'visualEvidence':['run/staging/root-S-spatial-full.jpg','run/staging/root-S-spatial-legs.jpg'],'independentStaticReview':'Root inspected current full16 full-body and leg contact sheets plus returned native images. S05 rejected enlarged-head outputs; final S05 derived from correct S06 identity; no pixel leg compositing.','limitations':['Actual normal-speed and quarter-speed browser review still pending.','Alpha lower bounds used only to locate suspected height inconsistency; contact and support anatomy judged visually.'],'clientValidated':False}
save(R/'audit/contact-S-review.json',contact)
reviews=read(R/'review.json');phase=read(R/'run/S/grounding-review.json')
for n,f in enumerate(frames,1):
 pair=pairs[(n-1)//2];slot=f['file'][:-4]
 reviews[slot]={**reviews.get(slot,{}),'sha256':f['sha256'],'visualStatus':'static_pending_root_preview','latestRequirement':'audit/spatial-contact-requirement.json','contactReview':'audit/contact-S-review.json'}
 row=phase['frames'][n-1];meta=read(R/(f['file']+'.generation.json'))
 row.update({'file':f['file'],'frame':n,'sha256':f['sha256'],'selectedNative':meta['derivedFrom']['file'],'durationMs':75,'phase':pair['position'],'supportLeg':pair['supportLeg'],'observation':pair['observations'],'reviewStatus':'static_pending_root_preview'})
phase.update({'status':'static_pending_root_preview','spatialContactReview':'audit/contact-S-review.json','positionPairs':pairs,'contactSpans':contact['contacts'],'selectedCycleMs':1200,'durationsMs':[75]*16,'clientValidated':False})
save(R/'run/S/grounding-review.json',phase);save(R/'review.json',reviews)
print(json.dumps({'promoted':len(selection),'direction':'S','status':'static_pending_root_preview'}))
