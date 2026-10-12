from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast'); i='r04_c12_p03_04_v5'
p=z/'guides'/f'{i}.anchored-layout-only.png'
a=np.array(Image.open(p).convert('RGB'))
x=np.arange(a.shape[1])[None,:]
b=a[:,:,2].astype(float);r=a[:,:,0].astype(float);g=a[:,:,1].astype(float)
mask=(x>=230)&(b>r*1.25)&(b>g*1.08)
a[mask]=[180,180,180]
q=z/'guides'/f'{i}.roof-replacement-region.png';Image.fromarray(a).save(q)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={'operation':'mechanical blue-region omission marker for generation guide only','source':p.as_posix(),'sourceSha256':sha(p),'condition':'x>=230 and B>R*1.25 and B>G*1.08','fill':[180,180,180],'markedPixels':int(mask.sum()),'finalArt':False,'noResampling':True,'output':q.as_posix(),'sha256':sha(q)}
q.with_suffix('.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
f=z/'prompts'/f'{i}.inputs.json'; refs=json.loads(f.read_text(encoding='utf-8-sig'));refs[0]={'file':q.as_posix(),'sha256':sha(q),'role':'EDIT TARGET generation guide only: neutral gray indicates entire blue roof surface to regenerate; exact left strip and gold/red architecture preserved'};f.write_text(json.dumps(refs,indent=2),encoding='utf-8')
print(json.dumps(d))

