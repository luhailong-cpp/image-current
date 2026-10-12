import json,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
r=Path(__file__).resolve().parents[1]
inv=json.loads((r/'inventory-hit.json').read_text(encoding='utf-8-sig'))
phases=[
('左脚承重延续','a5实际附09动作参考，近左前鞋平底延续16帧承重，远右后脚悬空；主代理全尺寸实看鞋平、两腿不串位、持手正确，单图接受'),
('左脚屈膝承重','近左腿膝下压、鞋底平，远右脚抬起'),
('左脚单支撑，右腿过腿','近左腿在身体下支撑，远右膝在viewer左抬过；鞋头沿SW'),
('左脚晚支撑，右腿前摆','a2真实重画远右腿向前；近左后鞋前掌朝下，前远右鞋悬空'),
('左脚蹬离，右腿前摆','a2后近左腿伸展、前掌向下蹬离；远右鞋前伸亮出鞋底'),
('短飞行，右前左后','近左后踝重建后，后鞋跟在右上鞋尖左下；前远右鞋也朝SW'),
('右脚初接触','a5实际附09动作参照，前远右鞋由露整块鞋底改为近乎平底接触，后近左脚保持悬空；两鞋顺SW'),
('右脚落地承重压缩','a5前远右鞋平底、膝踝弯曲，后近左脚悬空；非下移贴地，头位稍高待连续复核'),
('右脚承重延续','前远右鞋已经平底，延续08承重，后近左腿收起；该帧保留现有正确鞋姿，不重复重画'),
('右脚屈膝承重','前远右鞋平底，膝位于身下，后近左脚悬空'),
('右脚单支撑，左腿过腿','a3真实重画：近左大腿从viewer右髋向前抬膝，前景鞋悬空；远右腿在骨盆下单支撑。主代理已独立实看局部修正通过。'),
('右脚晚支撑，左腿前摆','a2近左大腿从viewer右髋向左前穿过，远右后鞋前掌下指支撑'),
('右脚蹬离，左腿前摆','a2远右腿在后伸展，前掌下指；近左前鞋抬起可见底'),
('短飞行，左前右后','近左腿前伸、远右后腿收起；后踝联动修正成鞋头左下'),
('左脚初接触','a6实际附09动作参照，前近左鞋近乎平底接触、仅见窄金边；远右后脚仍悬空，鞋尖顺SW'),
('左脚落地承重压缩','a4前近左鞋平底且膝踝承重，后远右脚收起；两鞋顺SW，非下移贴地')
]
dur=[75]*16
j={'schema':1,'action':'run','direction':'SW','updatedAt':datetime.datetime.now(ZoneInfo('America/New_York')).isoformat(),'reviewMethod':'逐帧实际查看生成结果和整画布联系表；未将提示词当验收；最终正常/慢速播放由主代理完成','userCriterion':'没有整套已通过方向；逐图判断真实鞋跟到鞋尖轴向，只改外转，不仅缩腿距。未附07参考图。','root':{'declared':[512,920],'registration':'仅整1254画布统一1024导出，无bbox裁切缩放及最低脚对齐。局部编辑造成的意外放大另以AI纯相机修订，未与鞋向目标混在同次调用。'},'timing':{},'frames':[],'unresolved':['主代理需正常与慢速实播确认头身物理尺度/根点起伏连续，特别相机修订后的05→06→07、08→09→10、13→14→15→16','03/11为两次过腿相位，但近远髋遮挡仍需在动态中持续追踪左右腿，不能仅依据道具方向判腿身份','01/09接触到02/10承重的膝踝压缩须实播确认；静态支点不等于落地感通过','本机无客户端，位移同步/滑步和游戏真实尺寸未接入验收'],'clientStatus':'未接入，本机无客户端'}
j['timing']={'status':'用户最新明确要求，素材预览采用；客户端未接入','cycle_ms':1200,'frame_ms':75,'durations_ms':dur,'phase_weights_applied':False,'fast_presets_removed':True,'slow_playback':'0.25x'}
j['userCriterion']='逐图检查 heel-to-toe 轴，只修真实外撇；用户最新授权09竹弓少女当前版本作动作参照，已只读查看且实际附入S/SW共11张落地及承重延续修订；未附07。'
j['root']['registration']='完整原生1254画布统一导出1024；无bbox/最低脚贴地。九张90%试版经实看后已撤回；07/08/15/16随后按09动作参照真实局部重画。'
j['unresolved']=['完整1200ms循环、慢放及四肢连续轨迹由主代理最终实播复核','重点复核05→06→07、08→09→10及13→14→15→16的头身体量与承重连续；静态通过不等于整体起伏通过','本分工未接入或运行客户端验收，位移同步/滑步未验收']
j['clientStatus']='本分工未接入或运行客户端验收'
for f in sorted((f for f in inv['frames'] if f['action']=='run' and f['direction']=='SW'),key=lambda f:f['frame']):
    n=f['frame'];row=dict(f);row.update(actual_phase=phases[n-1][0],contact_evidence=phases[n-1][1],toe_axis_review='鞋跟与鞋尖方向已实看；当前以左下前进方向为主，未见此前后鞋明显朝右下反向外转',review_status='静态候选；连续性、尺度、接地感待主代理实播',suggested_duration_ms=dur[n-1])
    if n in (1,7,8,15,16):
        row['review_status']='主代理独立局部静态接受；完整序列待主代理复核'
    j['frames'].append(row)
p=r/'work/run-SW/run-SW-grounding-review-20261003.json'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(p),'count':len(j['frames']),'cycle_ms':sum(dur)},ensure_ascii=False))

