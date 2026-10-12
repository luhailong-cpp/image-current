from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
def edit(rel, fn):
 p=R/rel;s=p.read_text(encoding='utf-8');p.write_text(fn(s),encoding='utf-8')
edit('tools/build_current_review.py', lambda s: re.sub(r'dur=\[[^\n]+\]', 'dur=[75]*16', s, count=1).replace("'status':'trial_not_client_approved'","'status':'normal_preview_user_selected_client_unconfirmed'").replace("'uniformCycleMs':720","'uniformCycleMs':1200").replace("'comparisonsMs':[480,640,720,800]","'comparisonsMs':[]").replace("'reason':'按实图初触E01/E08各隔360ms；右离地E06于280ms、左离地E14于640ms，两段腾空各80ms。承重多停留，仅试播。'","'reason':'用户最新指定16帧均匀75ms，整圈1200ms；正常1倍不再使用旧快速档或相位权重。实际接触仍按当前图观察，E01至E08为525ms，E08至下圈E01为675ms。'").replace("'formallyAdopted':False","'formallyAdopted':False,'offlineDefaultApplied':True").replace("'offsetMs':360","'offsetMs':525").replace("'offsetMs':280","'offsetMs':375").replace("'offsetMs':640","'offsetMs':975"))
edit('tools/build_grounding_preview.py',lambda s:s.replace("'uniformCycleMs': 720","'uniformCycleMs': 1200").replace("'cycleComparisonsMs': [480, 640, 720, 800]","'cycleComparisonsMs': []"))
edit('tools/build_delivery.py',lambda s:s.replace('"count": 16, "frame_ms": 45},\n    "hit"','"count": 16, "frame_ms": 75},\n    "hit"').replace('preserve its reviewed per-frame pacing instead of restoring 480 ms.','use the user-selected uniform 75 ms instead of old fast timings.'))
edit('tools/verify_candidates.py',lambda s:s.replace("report['timingTotalMs']==720","report['timingTotalMs']==1200").replace("assert report['rightToLeftContactMs']==report['leftToRightContactMs']==360","assert selection['timing']['frameDurationsMs']==[75]*16\nassert report['rightToLeftContactMs']==525 and report['leftToRightContactMs']==675"))
edit('tools/export_playback.py',lambda s:s.replace('run-E-1x-720ms.webp','run-E-1x-1200ms.webp'))
p=R/'preview/player.js';s=p.read_text(encoding='utf-8')
a=s.index('function durationsFor(s) {');b=s.index('\nfunction frameAt(',a)
s=s[:a]+"function durationsFor(s) { return Array(16).fill(75); }\n"+s[b:]
a=s.index('for (const total of [480,640,720,800])')
b=s.index('\nfunction resize()',a)
s=s[:a]+"const nativeLane = createLane('native-lane','正常跑步 · 1200 ms / 圈','16帧 · 每帧75 ms · 当前修稿',durationsFor(selection),true);"+s[b:]
a=s.index("  const d=s.timing?.frameDurationsMs;")
b=s.index('\n  return s;',a)
s=s[:a]+"  const d=s.timing?.frameDurationsMs;\n  if(!Array.isArray(d)||d.length!==16||d.some(n=>n!==75))throw Error('当前跑步统一16帧 × 75ms = 1200ms，请先更新选择清单');"+s[b:]
a=s.index("  $('native-summary').textContent=");b=s.index("\n  $('root-summary')",a)
s=s[:a]+"  $('native-summary').textContent=\u0060\u0024{count} / 16 槽有选图。正常1倍：1200 ms / 圈，16帧每帧75 ms；完整16帧连续回环，首尾不额外停顿。客户端速度尚未接入确认。\u0060;"+s[b:]
p.write_text(s,encoding='utf-8')
p=R/'preview/index.html';s=p.read_text(encoding='utf-8')
a=s.index('<details>\n<summary>节奏对照</summary>');b=s.index('</details>',a)+len('</details>')
s=s[:a]+s[b:]
s=s.replace('默认1倍速，720毫秒一圈。当前E向修稿，尚未完成游戏内验收。','正常1倍：1200毫秒一圈，16帧每帧75毫秒。当前E向修稿；游戏内速度尚未接入。').replace('当前16槽复核：循环仍不通过','当前16槽视觉复核')
a=s.index('<div class="warning">');b=s.index('<div class="native-note">',a)
s=s[:a]+'<p class="smallprint">当前正常跑步统一1200ms/圈、75ms/帧。已移除旧快速档和分相位权重；慢放为0.25倍。地面线仅供检查，不移动角色；缺失槽保持空白。受击、普攻与施法时长不受本次调整影响。</p>\n'+s[b:]
p.write_text(s,encoding='utf-8')
timing={'characterId':R.name,'run':{'directions':['N','NE','E','SE','S','SW','W','NW'],'frameCount':16,'frameMs':75,'cycleMs':1200,'frameDurationsMs':[75]*16,'playbackRates':[1,0.25],'phaseWeightsApplied':False,'offlineDefaultApplied':True,'clientTimingConfirmed':False},'hit':{'frameCount':6,'frameMs':40,'cycleMs':240},'attack':{'frameCount':12,'frameMs':30,'cycleMs':360},'cast':{'frameCount':16,'frameMs':45,'cycleMs':720},'clientIntegrated':False}
(R/'animation-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Active E preview and all run defaults now 1200ms/75ms; combat unchanged.')

