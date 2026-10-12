from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent/'finish-20261011'
D.mkdir(exist_ok=True)
C=D.parents[1]/'candidates/r08_c14.candidate.png'
im=Image.open(C).convert('RGB')
box=[397,2143,1651,3397]
out=D/'m01-stone-input.png'
assert not out.exists()
im.crop(box).save(out)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
Path(str(out)+'.generation.json').write_text(json.dumps({'file':str(out),'sha256':h(out),'assetRole':'native-size repair edit input only','source':str(C),'sourceSha256':h(C),'crop':box,'resized':False},indent=2),encoding='utf-8')
print(out)

