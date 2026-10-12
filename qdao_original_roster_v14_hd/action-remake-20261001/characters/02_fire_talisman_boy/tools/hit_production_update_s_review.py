import json,hashlib,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
r=Path(__file__).resolve().parents[1]
p=r/'work/run-S/run-S-grounding-review-20261003.json'
j=json.loads(p.read_text(encoding='utf-8-sig'))
inv=json.loads((r/'inventory-hit.json').read_text(encoding='utf-8-sig'))
rows={f['frame']:f for f in inv['frames'] if f['action']=='run' and f['direction']=='S'}
for f in j['frames']:
    f.update(rows[f['frame']])
    f['toe_axis_review']='前鞋鞋尖向画面下方，未见明确左右外八；后脚因抬跟可见鞋顶，单帧暂未见明显反向'
    f['review_status']='静态候选，连续性及比例待主代理实播'
    if f['frame'] == 4:
        f.update(actual_phase='左腿后方支撑到蹬地、右腿前摆',contact_evidence='a2 后左鞋前掌下指、后跟抬起；右前鞋底朝镜头悬空；比上一版支点更清楚',review_status='已重画晚支撑，动态承重与相邻帧需实播')
    if f['frame'] == 12:
        f.update(actual_phase='右腿后方支撑到蹬地、左腿前摆',contact_evidence='a2 后右鞋位于 viewer 左下且前掌下指；左前鞋抬起；两鞋不再互相外岔',review_status='已重画晚支撑，动态承重与相邻帧需实播')
    if f['frame'] == 13:
        f.update(contact_evidence='a3 后右鞋由向 viewer 左外撇改成鞋尖向正前下方，前左鞋悬空；后前掌朝下',toe_axis_review='后鞋外撇已局部修正；两鞋长轴均朝前，无横向外岔',review_status='鞋向静态通过，蹬离力度与过渡待实播')
    if f['frame'] in [14]:
        f['review_status']='鞋底后端轮廓为可解释的鞋跟投影，未见多脚；动态轮廓连续性仍待实播'
    if f['frame'] in (7,15):
        side='右' if f['frame']==7 else '左'
        f.update(actual_phase=side+'脚初接触',contact_evidence='a2实际附09对应动作参考，前鞋由大块鞋底朝镜头改为窄金底边/近乎平底，后脚仍悬空；脚尖正前，膝踝连贯',review_status='新接触局部实看，动态连接待主代理复核')
    if f['frame'] in (8,16):
        side='右' if f['frame']==8 else '左'
        f.update(actual_phase=side+'脚落地承重压缩',contact_evidence='a2前鞋平底，支撑膝及踝弯曲；后脚收起，双膝鞋尖顺S；真实AI局部重画非下移贴地',review_status='新承重局部实看，动态连接待主代理复核')
    if f['frame'] in (1,9):
        side='左' if f['frame']==1 else '右'
        attempt='a3' if f['frame']==1 else 'a5'
        f.update(actual_phase=side+'脚承重延续',contact_evidence=attempt+'实际附09动作参考，前鞋平底延续上一帧承重，后鞋悬空；不再抬前掌重复落地。主代理全尺寸实看鞋平、两腿不串位、持手正确。',review_status='主代理独立单图接受；完整序列待主代理复核')
    if f['frame'] in (7,8,15,16):
        f['review_status']='主代理独立确认双腿和落平动作成立；完整序列待主代理复核'
    f['suggested_duration_ms']=75
j['timing']={'status':'用户最新明确要求，素材预览采用；客户端未接入','cycle_ms':1200,'frame_ms':75,'durations_ms':[75]*16,'phase_weights_applied':False,'fast_presets_removed':True,'slow_playback':'0.25x'}
j['updatedAt']=datetime.datetime.now(ZoneInfo('America/New_York')).isoformat()
j['userCriterion']='逐图检查 heel-to-toe 轴，只修真实外撇；用户最新授权09竹弓少女当前版本作动作参照，已只读查看且实际附入S/SW共11张落地及承重延续修订；未附07。'
j['unresolved']=['完整1200ms循环、慢放及四肢连续轨迹由主代理最终实播复核','S01新结果单图通过但整体略放大，须对照16→01→02；不自动再生或像素配准','本分工未接入或运行客户端验收，位移速度/滑步未验收']
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'updated':str(p),'count':len(j['frames']),'sum_ms':sum(j['timing']['durations_ms'])},ensure_ascii=False))

