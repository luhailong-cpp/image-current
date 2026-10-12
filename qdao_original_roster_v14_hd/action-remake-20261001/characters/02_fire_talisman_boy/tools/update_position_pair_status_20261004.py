from pathlib import Path
import json
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
latest='同一支撑脚连续接地，逐步变化的相对位置各2张独立姿态（150ms）；4段8帧后换另一脚，共16×75ms=1200ms。位置沿行进轴判断，鞋尖不逐步向外撇。'
p=R/'STATUS.md'
p.write_text('# 02 火符少年当前进度\n\n2026-10-04：用户最新澄清已取代中间4帧/两侧2帧方案，无需继续等空间含义回复。\n\n'+latest+'\n\n跑步128张重新排相位并修必要姿态，当前未完成。现有196张库存不能作为新方案通过。受击12、普攻24、施法32保留此前离线复核。新关键姿态见 previews/grounding-new-keyposes-20261004.png（上排旧正式、下排新候选）。客户端未接入。\n',encoding='utf-8')
p=R/'reviews'/'final-review.json';review=json.loads(p.read_text(encoding='utf-8-sig'))
review['knownUnresolvedArtFailures']=['最新每两帧一个接地相对位置、同脚连续8帧的跑步要求正在制作与复核；未完成。']
review['latestGroundingRequirement']=latest
p.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'tools'/'write_handoff.py';s=p.read_text(encoding='utf-8');s=s.replace('196张旧正式帧在库；跑步接地空间分配与承重姿态正在修订，中间4帧、两侧各2帧尚待空间含义确认','196张旧正式帧在库；按最新同脚连续8帧、每两帧一个位置段修订跑步，尚未完成');p.write_text(s,encoding='utf-8')
for name in ['tools/run-grounding-template.html','previews/run-grounding.html']:
 p=R/name;s=p.read_text(encoding='utf-8');s=s.replace('八方向连续四帧接地修订中','八方向按每两帧一个接地位置段修订中').replace('连续四帧接地修订中','两帧位置段修订中').replace('接地空间分配修订中','两帧位置段修订中')
 p.write_text(s,encoding='utf-8')
print({'status':'production_in_progress','timing':'16 x 75 ms = 1200 ms'})
