from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'source-selection.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d['slots']['run/NE/03']='generation/run-NE-03-v4/native.png'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'tools/review_n_sequence.py'
s=p.read_text(encoding='utf-8').replace("'timing':{'trialCycleMs':720,'comparisonCycleMs':[480,640,720,800],'selectedCycleMs':None}","'timing':{'frameMs':75,'selectedCycleMs':1200,'phaseWeightsApplied':False}")
p.write_text(s,encoding='utf-8')
for name in ['update_handoff_wording.py','update_preview_timing_labels.py']:
 (R/'tools'/name).write_text("from pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).with_name('build_current_player.py')),run_name='__main__')\n",encoding='utf-8')

