from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'run/E/registration.json';j=json.loads(p.read_text(encoding='utf-8'))
for row in j['frames']:
 if row['file']=='run/E/13.png':
  row['sha256']=hashlib.sha256((R/row['file']).read_bytes()).hexdigest()
  row['srcRoot']=[635,980]
  row['basis']='v4早腾空补画；解剖髋根635，E向统一地面980，无逐帧脚底吸附。'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')

