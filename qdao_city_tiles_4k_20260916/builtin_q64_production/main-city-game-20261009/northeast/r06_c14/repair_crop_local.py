from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa'/'native-repairs';Q.mkdir(parents=True,exist_ok=True)
source=T/'qa'/'top-half'/'top-half.png'; target=Q/'m01-input.png'
im=Image.open(source).convert('RGB');im.crop((2842,700,4096,1954)).save(target)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(Q/'m01-input.json').write_text(json.dumps({'file':str(target),'sha256':sha(target),'source':str(source),'sourceSha256':sha(source),'origin':[2842,700],'size':[1254,1254],'operation':'integer crop; no resize'},indent=2),encoding='utf-8')

