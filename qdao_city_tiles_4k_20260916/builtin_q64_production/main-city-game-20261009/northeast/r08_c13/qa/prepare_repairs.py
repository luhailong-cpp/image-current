from pathlib import Path
from PIL import Image
import json,hashlib
TILE=Path(__file__).resolve().parent.parent
BASE=TILE/'qa/core-baseline/df217b3c44d2eb2195d0/r08_c13-core-baseline.candidate.png'
OUT=TILE/'qa/finish-20261011'
for d in ['context','source','prompts','receipts','records','masks','review']:(OUT/d).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(BASE).convert('RGB')
im.resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/'review/baseline-preview-25pct.png')
box=[1421,2445,2675,3699];f=OUT/'context/road-junction.png';im.crop(box).save(f)
record={'tile':'r08_c13','source':str(BASE),'sourceSha256':sha(BASE),'contextTileBox':box,'contextWorldBox':[box[0]+49152,box[1]+28672,box[2]+49152,box[3]+28672],'file':str(f),'sha256':sha(f),'dimensions':[1254,1254],'resized':False,'operation':'integer crop from full16core baseline','issue':'P2 angular misregistration in single diagonal-to-horizontal road border'}
(OUT/'records/road-context.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(f)
