import json,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
r=Path(__file__).resolve().parents[1]
inv=json.loads((r/'inventory-hit.json').read_text(encoding='utf-8-sig'))
j={'schema':1,'action':'hit','updatedAt':datetime.datetime.now(ZoneInfo('America/New_York')).isoformat(),'criterion':'逐帧看鞋跟到鞋尖方向及踝连接，只修真实外转，不以两腿间距为标准。','method':'已实际查看全部12张当前native全图及E/W联系表；单帧静态检查。动态播放由主代理负责。','clientStatus':'本机无客户端，未接入','timing':'保持每方向6帧、每帧40ms，不受跑步速度试验影响','frames':[]}
for f in sorted((f for f in inv['frames'] if f['action']=='hit'),key=lambda f:(f['direction'],f['frame'])):
    row=dict(f)
    if f['direction']=='W':
        row['toe_axis_observation']='前后鞋均以向屏幕左为主；近脚略有正面透视，鞋跟在右、鞋头在左，未见朝反侧的外八'
        row['decision']='保留当前画面，不因透视差异机械重画'
    elif f['frame']==6:
        row['toe_axis_observation']='旧版后鞋较正面；20261003局部重画后，两鞋侧面长轴均朝右，踝及双腿仍连贯'
        row['decision']='使用新鞋向修订；等待与05的动态衔接复核'
    else:
        row['toe_axis_observation']='两鞋均以向屏幕右为主；后鞋略右下、前鞋较平，属于轻微透视差，未见明显反向外撇'
        row['decision']='保留当前画面'
    if f['direction']=='E' and f['frame'] in (4,6):
        row['static_identity_check']='此前近右肩错误连到铃手的判断已撤销。本轮重画完整近右肩-袖-腕-符手链，远左铃臂置于后层；E04额外清除了旧第三空袖。主代理20261003独立实看：两条完整手链、近右扇远左铃、五卡和两鞋E向，局部修正通过。'
        row['visual_status']='hand_chain_independently_reviewed_sequence_pending'
    elif f['direction']=='E' and f['frame']==5:
        row['static_identity_check']='完整近右扇臂与后左铃臂保持；20261003局部清除扇后无手的第三空袖口。主代理独立实看：两条完整手链、近右扇远左铃、五卡和两鞋E向，局部修正通过。'
        row['visual_status']='hand_chain_independently_reviewed_sequence_pending'
    else:
        row['static_identity_check']='当前静态画面见五张红符扇（个别最外张窄叠露边）及铜铃；此前静态检查未见增肢或离体道具，完整手链仍以独立复核为准'
        row['visual_status']='toe_axis_static_reviewed_sequence_pending'
    j['frames'].append(row)
j['unresolved']=['原始画布各帧主体尺度/落点存在轻微差异，仍需正常尺寸与慢速连续验收','本记录不代表客户端播放通过']
p=r/'work/hit/hit-foot-axis-review-20261003.json'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(p))

