from pathlib import Path
import json,hashlib
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
rows=[]
for n in [3,11]:
 src=R/'run/staging'/f'run-E-{n:02d}-contact-v2.png'
 dest=R/'run/E'/f'{n:02d}.png'
 run(src,dest)
 rows.append({'file':dest.relative_to(R).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'srcRoot':[630,980],'basis':'Preserved original composition and anatomical root; local supporting knee/ankle edit only, no sole alignment or whole-figure translation.'})
p=R/'run/E/contact-registration.json'
p.write_text(json.dumps({'globalScale':.8,'targetRoot':[512,942],'frames':rows},indent=2),encoding='utf-8')
apply(p)
