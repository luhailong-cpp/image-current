from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
reg=json.loads((R/'run/E/registration.json').read_text(encoding='utf-8'))
rows=[]
for n in [6,8,9,12,14,15,16]:
    p=R/'run/E'/f'{n:02d}.png'
    row=next(x for x in reg['frames'] if x['file']==f'run/E/{n:02d}.png').copy()
    meta=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
    current=hashlib.sha256(p.read_bytes()).hexdigest()
    row['sha256']=meta.get('registrationTransform',{}).get('inputSha256',current) if meta.get('registrationTransform',{}).get('outputSha256')==current else current
    row['basis']='09竹弓同方向蹬离/前后腿飞行参考编辑；保留原生构图与原人工髋根注册坐标；无逐帧贴底。'
    rows.append(row)
reg['frames']=rows
reg['updatedAt']=datetime.now(timezone.utc).isoformat()
(R/'run/E/bamboo-registration.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
