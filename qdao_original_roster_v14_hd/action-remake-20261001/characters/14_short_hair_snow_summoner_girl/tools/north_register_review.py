from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
xs={
'N':[535,535,525,550,540,525,530,550,530,535,535,550,530,530,545,535],
'NE':[530,535,545,530,530,550,555,565,535,525,525,525,525,535,530,530],
'NW':[550,550,565,560,555,560,555,565,545,535,550,555,545,550,540,560]}
ys={'N':968,'NE':968,'NW':960}
phases={
'N':['left_contact','left_absorb','left_support_compress','left_support_exit','left_toe_off','flight_right_knee_drive','flight_right_approach','right_approach','right_contact','right_absorb','right_support_compress','right_support_exit','right_toe_off','flight_left_knee_drive','flight_left_approach','left_approach'],
'NE':['left_contact','left_absorb','left_support_compress','left_support_exit','left_toe_off','flight_right_approach','right_approach','right_approach','right_contact','right_absorb','right_support_exit','right_toe_off','right_toe_off','flight_left_knee_drive','left_approach','left_approach'],
'NW':['left_approach','left_contact_absorb','left_support','left_support_exit','left_toe_off','flight_right_drive','right_approach','right_approach','right_contact','right_absorb','right_support','right_support_exit','right_toe_off','flight_left_drive','left_approach','left_approach']}
supportnotes={
'N':'正后视：01–05左腿在画面左侧承重/蹬离；09–13右腿在画面右侧承重/蹬离。06/07与14/15已独立AI补画双腿屈膝短腾空，不以最低像素作相位依据。',
'NE':'后右斜视：01–05左腿下落/承重，09–13右腿下落/承重。01–03、12–16二/三版修正早换侧；14先左膝抬进，15–16左脚降落。NE07/08为伸腿接近落地而非最高腾空。',
'NW':'后左斜视：02–05近侧左腿下伸承重；09–11近侧左大腿折起跨前景，远侧右小腿在其后下伸承重；不是仅由低脚屏幕左右判侧。12–13右腿继续后蹬，14–16左腿前摆；01是接近落地。'}
report={'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'scope':['run/N','run/NE','run/NW'],'count':48,
'stage':'generation_export_and_manual_static_limb_review_complete; parent_global_registration_dynamic_review_next',
'proof':'每槽位由独立内置image_gen请求生成，逐图真请求/回执/native SHA关联正式1024RGBA派生记录。实际模型/质量工具未披露为null。',
'timingRecommendation':{'cycleMs':720,'frameMs':[45]*16,'reason':'先采用720ms均匀对照，帧上真实支撑/飞行已按像素复核；根任务可按最终动态承重视觉微调，未改客户端。'},
'criteria':'按鞋掌长轴、足踝和膝关节连接、行进方向判断外转；不把画面中腿距离或露鞋底等同外八，也不把任何其他角色/方向自动算通过。',
'frames':[],'notes':supportnotes,'remainingChecks':['由根任务统一0.8并复核正常720ms、慢速和循环边界','N03/11压膝版与相邻帧的头幅/足底小幅差异请重点复验；不得逐帧贴地修正','离线素材不能宣称已通过客户端位移、世界根点和滑步测试']}
for d in xs:
 frames=[]
 for i,x in enumerate(xs[d],1):
  p=ROOT/'run'/d/f'{i:02d}.png'; h=hashlib.sha256(p.read_bytes()).hexdigest()
  im=Image.open(p)
  assert im.size==(1024,1024) and im.mode=='RGBA'
  phase=phases[d][i-1]
  side=('left' if phase.startswith('left_') else 'right') if any(s in phase for s in ['contact','absorb','support','toe_off']) else None
  note=supportnotes[d]
  f={'file':p.relative_to(ROOT).as_posix(),'sha256':h,'srcRoot':[x,ys[d]],
     'basis':'人工按髋中心及腿根对完整单图与16帧连图判定x；同方向整组承重面y固定，包含近远透视及短腾空，不取逐帧最低像素。',
     'confidence':'manual approximately +/-15px; whole direction common ground plane'}
  frames.append(f)
  deriv=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
  report['frames'].append({'file':f['file'],'sha256':h,'selectedNative':deriv['derivedFrom']['file'],'phase':phases[d][i-1],
    'supportSide':side,'hands':'左臂抱一只白狐；右袖肩肘连接至托蓝雪花的右掌，未见额外肢体或断腕。',
    'footAxis':'保留，鞋掌与自身膝踝及该向行进方向一致；屈膝回收时露鞋底属于俯仰，不作为外八。',
    'identity':'短白发/毛耳/左发饰/白紫短袍/后紫蝴蝶结；无背面狐脸腰扣、无少女尾巴。',
    'reviewStatus':'manual_static_checked_pending_parent_animation'})
 out={'schemaVersion':1,'coordinateSpace':'whole-canvas1024 before global normalization','globalScale':0.8,'targetRoot':[512,942],
      'applyTransform':False,'method':f'manual anatomical hip-root projection; common virtual ground y{ys[d]} for complete {d} cycle','frames':frames}
 (ROOT/'run'/d/'registration.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'run'/'north-phase-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':len(report['frames']),'registrationGrounds':ys,'uniqueSHA':len({f['sha256'] for f in report['frames']})}))

