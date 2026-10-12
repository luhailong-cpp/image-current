from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'source-selection.json'
s=json.loads(p.read_text(encoding='utf-8-sig'));s['slots']['run/NE/06']='generation/run-NE-06-v5/native.png'
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'candidate/battle-registration.json'
c=json.loads(p.read_text(encoding='utf-8-sig'))
c['groups']['attack/E']={'translation':[53,160],'basis':'Fixed common native pelvis-ground x670,y1140; original lower-body pose variations remain visible for review.'}
c['groups']['attack/W']={'translation':[0,174],'basis':'Fixed common native pelvis-ground x746.3,y1120; W04-08 known old floating stance is being repaired in native pose, never hidden by frame translations.'}
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Current timing metadata; old generation receipts remain untouched.
for name in ['run-S-grounding-review.json','run-N-grounding-review.json']:
 p=R/name
 if p.exists():
  d=json.loads(p.read_text(encoding='utf-8-sig'))
  d['currentTiming']={'cycleMs':1200,'frameMs':75,'uniform':True,'phaseWeightsApplied':False,'basis':'latest explicit user instruction'}
  d['timingHistoryNote']='Older trial weight values are historical observations only; current player never applies them.'
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

