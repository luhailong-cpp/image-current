from pathlib import Path
import json,hashlib
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
dest=R/'run/N/10.png'
run(R/'run/staging/run-N-10-root-v9.png',dest)
reg={'globalScale':.8,'targetRoot':[512,942],'frames':[{'file':'run/N/10.png','sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'srcRoot':[535,944],'basis':'v9 generated the same upper-body/hip/leg composition approx30 native pixels higher than v6/v8. Anatomical projected hip root follows that artwork translation: normalized y968 to944. Scale stays0.8, no sole detection or pose synthesis. Head, belt, knee and foot landmarks move together.'}]}
p=R/'run/N/root-v9-registration.json'
p.write_text(json.dumps(reg,indent=2),encoding='utf-8')
apply(p)
