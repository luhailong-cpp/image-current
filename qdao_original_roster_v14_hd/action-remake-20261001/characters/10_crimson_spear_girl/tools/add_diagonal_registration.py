from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'candidate/registration.json'
cfg=json.loads(p.read_text(encoding='utf-8-sig'))
cfg['directions']['SE']={'translation':[66,133],'basis':'Native SE shared pelvis x650 and virtual ground1180; fixed full direction. Longitudinal foot depth retained. No individual foot snap.'}
cfg['directions']['NE']={'translation':[-30,150],'basis':'Native NE shared pelvis x790 and virtual ground1155; fixed full direction. Trial; preserve joint-driven height changes.'}
cfg['directions']['SW']={'translation':[73,145],'basis':'Native SW common pelvis x640 and support ground1162 from independent 04 and12; direction-wide translation only. Trial.'}
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'source-selection.json'
sel=json.loads(p.read_text(encoding='utf-8-sig'))
sel['slots'].update({'run/NE/02':'generation/run-NE-02-v2/native.png','run/NE/03':'generation/run-NE-03-v3/native.png','run/SW/04':'generation/run-SW-04/native.png'})
p.write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

