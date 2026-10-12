"""Apply latest direct human timing instruction to current rebuild paths only."""
from pathlib import Path
from datetime import datetime,timezone
import json,re
R=Path(__file__).resolve().parents[1]
files=['tools/build_previews.py','tools/final_contacts.py','tools/merge_inventory.py','tools/write_handoff.py','tools/run-grounding-template.html','tools/finalize_full_limb_review_20261005.py','tools/publish_full_limb_status_20261005.py','tools/verify_final_delivery.py','tools/write_root_full_limb_review_20261005.py','previews/run-grounding.html']
for name in files:
 p=R/name;s=p.read_text(encoding='utf-8')
 for a,b in [('1200','960'),('4800','3840'),('75ms','60ms'),('uniform75','uniform60'),('x75','x60')]:s=s.replace(a,b)
 s=re.sub(r'\b75\b','60',s)
 s=s.replace('duration=[80,70]*8','duration=[60]*16').replace('GIF 10ms quantization alternates 80/70; HTML exact uniform60; total960','GIF and HTML uniform60ms, total960').replace('80/70ms alternating, total960; HTML uniform60ms','GIF and HTML uniform60ms, total960').replace('跑步80/70交替总960','跑步均匀60ms、总960').replace('60ms未采用','按2026-10-05本聊天最新用户要求采用60ms，覆盖旧75ms').replace('鞋頭','鞋头')
 p.write_text(s,encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
p=R/'animation-timing.json';doc=json.loads(p.read_text(encoding='utf-8'));doc['updatedAt']=now;doc['userConfirmedRunTiming']=True;doc['run'].update(frameMs=60,cycleMs=960,slowCycleMs=3840,frames=16,uniform=True);doc['userInstruction']='2026-10-05 本角色聊天：不是已经改成60ms 一帧了吗';p.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['inventory.json','animation-events.json','reviews/run-position-pairs-final-20261004.json']:
 p=R/name;doc=json.loads(p.read_text(encoding='utf-8'))
 if name=='inventory.json':doc['timing']['run'].update(frameMs=60,cycleMs=960)
 elif name=='animation-events.json':doc['actions']['run'].update(frameMs=60,adoptedCycleMs=960)
 else:doc['timing'].update(frameMs=60,cycleMs=960,slowCycleMs=3840);doc['timingOverride']='reviews/run-timing-20261005-60ms.json'
 p.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'reviews/run-timing-20261005-60ms.json').write_text(json.dumps({'adoptedAtUtc':now,'source':'Direct human message in this character chat','quote':'不是已经改成60ms 一帧了吗','previousRunFrameMs':75,'runFrameMs':60,'runFrames':16,'runCycleMs':960,'runSlowCycleMs':3840,'positionPairMs':120,'scope':'run only; hit40ms, attack30ms, cast45ms unchanged','precedence':'This latest direct human instruction overrides earlier shared README and other-thread75ms instructions. Historical generation receipts and old review evidence remain unchanged.','currentRebuildFiles':files,'clientIntegrated':False},ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'STATUS.md';s=p.read_text(encoding='utf-8');s=s.replace('# 02 火符少年当前进度','# 02 火符少年当前进度\n\n最新时序（2026-10-05）：按本聊天用户要求，跑步60ms/帧、16帧960ms、慢放3840ms；覆盖下方旧75ms记录。当前手脚修订收尾中。');p.write_text(s,encoding='utf-8')
print({'runFrameMs':60,'runCycleMs':960,'runSlowCycleMs':3840,'currentFilesUpdated':len(files)})
