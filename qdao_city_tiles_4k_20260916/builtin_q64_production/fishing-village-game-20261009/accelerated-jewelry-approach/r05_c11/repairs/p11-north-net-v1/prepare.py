from pathlib import Path
from PIL import Image
import json,hashlib
d=Path(__file__).resolve().parent;b=d.parents[2]
base=b/'r05_c11/native/p11-v1.png';guide=b/'r05_c11/guides/p11-v1-positional.png'
im=Image.open(base).convert('RGB');im.paste(Image.open(guide).crop((0,0,1254,230)),(0,0));im.save(d/'target-native.png')
data={'sources':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [base,guide]],'operation':'Restore exact approved upper230 native-context rows over p11-v1. Positional guide interior never used. No resize.','globalNativeBox':[40845,16269,42099,17523],'dimensions':[1254,1254]}
(d/'target-derivation.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
