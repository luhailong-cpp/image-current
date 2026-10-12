from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).resolve().parent
b=p.parents[2]
s=b/'r04_c11/candidate/r04_c11-4096-candidate-v1.png'
box=[640,2304,1894,3558]
Image.open(s).crop(box).save(p/'target-native.png')
(p/'target-derivation.json').write_text(json.dumps({'source':str(s),'sourceSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'tileBox':box,'globalBox':[41600,14592,42854,15846],'operation':'unscaled native crop','dimensions':[1254,1254]},indent=2),encoding='utf-8')
