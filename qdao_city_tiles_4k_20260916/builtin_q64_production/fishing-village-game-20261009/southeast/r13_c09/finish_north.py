import json
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'qa/final-north-boundary-evidence.json'
d=json.loads(p.read_text());d.update(status='owner_visual_pass_final_sources',nativeSegmentsInspected=4,geometryBlockingFindings=[],formalAccepted=False)
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
p=R/'qa/internal-review.json';d=json.loads(p.read_text());d['externalSeams']='north final four segments owner visually passed; remaining exterior and junctions pending neighboring tile completion and independent review';p.write_text(json.dumps(d,indent=2),encoding='utf-8')
