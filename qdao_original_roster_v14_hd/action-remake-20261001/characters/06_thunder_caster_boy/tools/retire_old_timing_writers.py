"""Retire old timing writers; keep their exact source and old audit rows as text."""
from pathlib import Path
import ast,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
names=['work/run_audit.py','work/run_finish_w_review.py','work/run_W_phase_review.py','work/run_timing_1200.py','work/run_review_ne.py','work/run_review_ew.py','work/run_refresh_legacy_review.py','work/run_phase_review_v2.py','tools/build_run_N_review.py']
changes=[]
for name in names:
 p=R/name;s=p.read_text(encoding='utf-8-sig')
 if 'RETIRED_20261005' in s:continue
 archive=R/'records'/(p.name+'.before-retirement-20261005.txt');archive.write_text(s,encoding='utf-8')
 tree=ast.parse(s);line=0
 for i,n in enumerate(tree.body):
  if (i==0 and isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)) or (isinstance(n,ast.ImportFrom) and n.module=='__future__'):line=n.end_lineno
  else:break
 lines=s.splitlines(keepends=True);lines.insert(line,'\n# RETIRED_20261005: direct human timing correction supersedes historical writers.\nraise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")\n')
 p.write_text(''.join(lines),encoding='utf-8');ast.parse(p.read_text(encoding='utf-8'))
 changes.append({'file':name,'priorSourceText':archive.relative_to(R).as_posix()})
for name in ['review/run_inventory.json','review/run_EW_inventory.json','review/run_NE_inventory.json']:
 p=R/name;g=json.loads(p.read_text(encoding='utf-8-sig'));g.update(deprecated=True,reason='Historical review snapshot; its rows and SHA are not current delivery references.',currentInventory='STATUS.json',currentPreviewManifest='preview/manifest.json',deprecatedAt=datetime.now(timezone.utc).isoformat())
 if name.endswith('/run_inventory.json'):
  g['scope']='Historical pointer only; current all196 delivery uses STATUS.json and preview/manifest.json';g['currentTiming']={'frameMs':60,'loopMs':960};g.pop('additionalInventory',None)
 p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'records/retired_timing_writers_20261005.json').write_text(json.dumps({'retiredAt':datetime.now(timezone.utc).isoformat(),'files':changes,'currentRunFrameMs':60,'currentRunCycleMs':960},ensure_ascii=False,indent=2),encoding='utf-8')
print('Retired '+str(len(changes))+' historical timing writers; inventory pointers marked historical.')

