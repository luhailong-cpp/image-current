from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];T=R/'tools'
for name in ['timing.py','build_run_preview.py','build_sequence_previews.py','build_overview.py','verify_final_delivery.py']:
 p=T/name;s=p.read_text(encoding='utf-8-sig')
 s=re.sub(r'(?<![0-9])1200(?![0-9])','960',s)
 s=re.sub(r'(?<![0-9])4800(?![0-9])','3840',s)
 s=re.sub(r'(?<![0-9])75(?![0-9])','60',s)
 if name in ['build_overview.py','verify_final_delivery.py']:s=s.replace('("slow",300)','("slow",240)')
 if name=='build_run_preview.py':
  s=s.replace('同一脚连续承重8帧：前落、身下、后侧、后蹬各2个独立姿态，然后换脚。','相位设计：前落、身下、后侧、后蹬各2帧，8帧换脚；长袍遮髋处不能仅凭标签确认腿别。')
  s=s.replace('接地脚序：','设计脚序：')
 p.write_text(s,encoding='utf-8')
p=T/'export_preview.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace('"durationMs": 75','"durationMs": 60').replace('1200ms','960ms').replace('4800ms','3840ms').replace('75ms','60ms')
p.write_text(s,encoding='utf-8')
p=T/'build_delivery.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace('material_complete=grounding_complete and axis_complete','full_body_complete=len(review["groups"])==14 and all(g.get("fullBodyReview",{}).get("offlineReviewed",False) for g in review["groups"])\nmaterial_complete=grounding_complete and axis_complete and full_body_complete')
s=s.replace('manifest["axisReviewed"]=axis_complete','manifest["axisReviewed"]=axis_complete\nmanifest["fullBodyReviewed"]=full_body_complete')
s=s.replace('state["axisReviewed"]=axis_complete','state["axisReviewed"]=axis_complete\nstate["fullBodyReviewed"]=full_body_complete\nif not full_body_complete:state["remaining"].insert(0,"最新全196帧手臂与整腿补审/60ms浏览器复核待完成")')
s=s.replace('1200ms','960ms').replace('75ms','60ms').replace('150ms','120ms').replace('600ms','480ms').replace('"runLoopMs":1200','"runLoopMs":960')
s=s.replace('同一支撑脚连续8帧，前落、身下、后侧、后蹬各2张独立姿态；再换另一脚同样8帧。','设计相位为同一支撑脚8帧，前落、身下、后侧、后蹬各2张独立姿态；再换脚8帧。表内左右腿为制作标签，长袍遮住髋连接时不能直接证明解剖腿别。')
s=s.replace('## 最新脚轴复核','## 上一轮脚轴复核')
insert="""fullbodylines=["","## 本轮全身补审及60ms同步","","196帧已逐图补审肩肘腕握持与髋下膝踝鞋轴可见链。仅run/E/07双臂提前回收造成单帧跳动，采用第二版局部AI编辑修复；另外195帧图片原样保留。长袖、头发、长袍遮挡的关节不宣称直接可见。","","跑步最新正常为16×60ms=960ms，4倍慢放16×240ms=3840ms，无尾帧额外停留。战斗受击40、普攻30、施法45ms不变。依据provenance/timing-user-override-20261005.json覆盖旧75ms要求。","","当前补审状态："+("已完成" if full_body_complete else "静态完成，浏览器复核待完成")+"。详细记录：hand-review-20261005/audit-*.json、provenance/full-body-edits-applied.json及provenance/full-body-reference-history.json。E07两次调用的提示词、实际输入、回执与SHA保留；目标GPT Image 2.5 Sunburst/max，实际型号/质量仍未披露。客户端未接入、未运行。"]
for name in ['MERGE_HANDOFF.md','STATUS.md']:
 with (ROOT/name).open('a',encoding='utf-8') as f:f.write('\\n'.join(fullbodylines)+'\\n')
"""
s=s.replace('for script in ["build_sequence_previews.py"',insert+'for script in ["build_sequence_previews.py"')
p.write_text(s,encoding='utf-8')
p=T/'verify_final_delivery.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace("assert st['axisReviewed'] and mf['axisReviewed']","assert st['axisReviewed'] and mf['axisReviewed']\nassert st['fullBodyReviewed'] and mf['fullBodyReviewed']")
s=s.replace("result['axisRevision']=", "result['fullBodyEdits']=rd(R/'provenance/full-body-edits-applied.json')['count']\nresult['fullBodyRetained']=196-result['fullBodyEdits']\nresult['fullBodyReviewed']=True\nresult['axisRevision']=")
p.write_text(s,encoding='utf-8')
tim=json.loads((R/'animation-timing.json').read_text(encoding='utf-8-sig'));tim['run'].update(defaultLoopMs=960,frameDurationMs=60,frameDurationsMs=[60]*16)
(R/'animation-timing.json').write_text(json.dumps(tim,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['timing.py','build_delivery.py','build_run_preview.py','build_sequence_previews.py','build_overview.py','export_preview.py','verify_final_delivery.py']:
 compile((T/name).read_text(encoding='utf-8'),str(T/name),'exec')
print('Current timing chain 60ms and full-body completion gates updated; syntax passed.')

