from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'candidate/registration.json'
cfg=json.loads(p.read_text(encoding='utf-8-sig'))
cfg['directions']['NW']={'translation':[66,135],'basis':'NW reviewed whole-direction pelvis/stance projection; diagonal travel ground preserves longitudinal depth. No per-frame lowest-foot alignment.'}
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

