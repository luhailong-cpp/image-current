from pathlib import Path
import json,hashlib
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
p=R/'run/E/registration.json'
j=json.loads(p.read_text(encoding='utf-8'))
xs={4:630,5:630,6:630,7:630,8:630,9:630,10:630}
for i in range(4,11):
 v=6 if i in (6,8,9) else 5
 src=R/'run/staging'/f'run-E-{i:02d}-v{v}-ground.png'
 target=R/'run/E'/f'{i:02d}.png'
 run(src,target)
 row=next(x for x in j['frames'] if x['file']==target.relative_to(R).as_posix())
 row['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
 row['srcRoot']=[xs[i],980]
 row['basis']='v5/v6真实膝踝支撑腾空与近右臂修复；人工髋根x630、全E统一源地面980，无逐帧贴底。'
j['status']='reviewed anatomy and root; final sequence review pending'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
apply(p)
