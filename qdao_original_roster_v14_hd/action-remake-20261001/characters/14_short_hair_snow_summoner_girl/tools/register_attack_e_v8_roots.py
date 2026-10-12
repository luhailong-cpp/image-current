from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];p=R/'attack/registration.json';j=json.loads(p.read_text(encoding='utf-8'))
xs=[550,547,565,520,505,515,515,555,555,565,555,560]
for row in j['frames']:
 if row['file'].startswith('attack/E/'):
  i=int(Path(row['file']).stem)-1
  row.update(sha256=hashlib.sha256((R/row['file']).read_bytes()).hexdigest(),srcRoot=[xs[i],980],basis='v7/v8手臂解剖修正版人工靴踝支撑中心；E新全组统一地面980，保留步幅与屈膝；不逐帧最低脚对齐。')
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')

