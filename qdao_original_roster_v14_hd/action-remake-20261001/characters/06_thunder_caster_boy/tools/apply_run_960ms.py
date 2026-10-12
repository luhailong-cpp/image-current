"""Apply direct user correction 2026-10-05: run 16*60=960ms. Historical evidence is retained."""
from pathlib import Path
import json,re
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
files=['build_preview.py','build_delivery.py','build_run_board.py','build_timing_grounding.py','timing_grounding_template.html','inspect_assets.py','consolidate_current_review.py','verify_delivery_files.py','write_final_handoff.py','refresh_delivery_review.py','finalize_current_review.py']
changed=[]
for name in files:
 p=R/'tools'/name;s=p.read_text(encoding='utf-8-sig');old=s
 for a,b in [('1200','960'),('4800','3840'),('75','60'),('150','120')]:
  s=re.sub(r'(?<![0-9a-fA-F])'+a+r'(?![0-9a-fA-F])',b,s)
 s=s.replace("'requestDate':'2026-10-04'","'requestDate':'2026-10-05'")
 if s!=old:p.write_text(s,encoding='utf-8');changed.append(name)
p=R/'animation-timing.json';g=json.loads(p.read_text(encoding='utf-8-sig'));g['run'].update(frameMs=60,cycleMs=960,durationsMs=[60]*16,slowCycleMs=3840,latestUserCorrection='2026-10-05 不是已经改成60ms一帧了吗');p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'tools/apply_run_1200ms.py').write_text('"""Retired timing migration; direct human correction supersedes75ms."""\nraise SystemExit("已退役：当前跑步60ms/帧、960ms/圈，请运行build_preview.py及build_delivery.py。")\n',encoding='utf-8')
record={'recordedAt':datetime.now(timezone.utc).isoformat(),'directUserMessage':'不是已经改成60ms 一帧了吗','previousFrameMs':75,'frameMs':60,'frameCount':16,'cycleMs':960,'slowFrameMs':240,'slowCycleMs':3840,'scope':'06 run only, hit40 attack30 cast45 unchanged','buildersUpdated':changed,'source':'direct human message in this character chat; overrides older batch README'}
(R/'records/run_timing_user_correction_20261005.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=True))
