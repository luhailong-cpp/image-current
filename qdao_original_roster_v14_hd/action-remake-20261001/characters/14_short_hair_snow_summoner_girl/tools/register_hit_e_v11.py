from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'hit/registration.json'
j=json.loads(p.read_text(encoding='utf-8'))
xs=[550,545,540,555,535,558]
for row in j['frames']:
 if row['file'].startswith('hit/E/'):
  i=int(Path(row['file']).stem)-1
  row.update(sha256=hashlib.sha256((R/row['file']).read_bytes()).hexdigest(),srcRoot=[xs[i],980],basis='v11侧身实图靴踝窗口人工复核；x取双踝支撑中心，E整组虚拟地面固定980，保留屈膝后仰，无逐帧最低脚贴地。',confidence='manual anatomical estimate +/-8px')
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')

