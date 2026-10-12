from pathlib import Path
from PIL import Image
import json,hashlib
b=Path(__file__).resolve().parents[1]
base=b/'native/p02_02.png'
top=b/'refinement/versions/tower-curl-v04/p01_02.png'
out=b/'refinement/p02_02.native-top-rebase.png'
assert not out.exists()
im=Image.open(base).convert('RGB')
im.paste(Image.open(top).crop((0,1024,1254,1254)),(0,0))
im.save(out)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={'base':str(base),'baseSha256':h(base),'top':str(top),'topSha256':h(top),'sourceCrop':[0,1024,1254,1254],'targetBox':[0,0,1254,230],'operation':'exact native pixel crop/paste seed only; no resampling','output':str(out),'outputSha256':h(out),'notFinalArt':True}
out.with_suffix('.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(str(out))
