from pathlib import Path
import json,hashlib
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
out=R/'run/E/11.png';run(R/'run/staging/run-E-11-v2-arm.png',out)
p=R/'run/E/registration.json';j=json.loads(p.read_text(encoding='utf-8'))
row=next(x for x in j['frames'] if x['file']=='run/E/11.png')
row.update({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'srcRoot':[630,980],'basis':'Right arm passing hip between forward and backward swing; support leg preserved; common E source ground980.'})
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');apply(p)
