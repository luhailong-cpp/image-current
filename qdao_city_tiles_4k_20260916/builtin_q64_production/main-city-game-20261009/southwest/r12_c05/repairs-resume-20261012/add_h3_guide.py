from pathlib import Path
from PIL import Image
import hashlib,json,sys
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
T=D/(sys.argv[1] if len(sys.argv)>1 else 'H3-3-blue-edge-gap-v01')
p=T/'request.json';r=json.loads(p.read_text());q=T/'QA-ROI-guide-not-final.png'
assert len(r['references'])==4
r['references'].append({'file':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'dimensions':list(Image.open(q).size),'role':'QA-only small repair rectangle; never final art'})
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
