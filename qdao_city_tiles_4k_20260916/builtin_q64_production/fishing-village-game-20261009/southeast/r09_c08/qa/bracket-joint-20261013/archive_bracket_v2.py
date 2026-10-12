from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Path('C:/Users/luyua/.codex/generated_images/01a13554-e65d-71e2-a119-8c3677ffd303/exec-e8437d87-81c7-4d21-abed-f4f8ab8fcd0b.png')
p=Q/'bracket-v2-raw.png';assert not p.exists();shutil.copyfile(src,p)
im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
g=dict(savedAtUtc=datetime.now(timezone.utc).isoformat(),tool='image_gen__imagegen',route='builtin',actualModel=None,
 actualQuality=None,file=str(p),sha256=sha(p),nativeDimensions=[1254,1254],sourcePath=str(src),
 prompt=str(Q/'bracket-v2.prompt.txt'),request=str(Q/'bracket-v2.request.json'),receipt=str(Q/'bracket-v2.receipt.json'),
 selected=False,operation='Byte-exact copy of actual builtin output')
(Q/'bracket-v2-raw.png.generation.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8')
im.crop([550,170,910,600]).save(Q/'bracket-v2-raw-boundary-100pct.png')
base=np.asarray(Image.open(Q/'joint-input-v1-1254.png').convert('RGB'));new=np.asarray(im)
profiles=[]
for y in [525,530,535,540,545,550]:
    pairs=[]
    for a in [base,new]:
        row=a[y,620:680].astype(int); m=(row[:,0]>120)&(row[:,0]>row[:,2]*1.5)&(row[:,1]>55)
        xs=np.where(m)[0]+620;pairs.append([int(xs[0]),int(xs[-1])] if len(xs) else [])
    profiles.append(dict(y=y,originalGoldRange=pairs[0],newGoldRange=pairs[1]))
(Q/'bracket-v2-shaft-profiles.json').write_text(json.dumps(profiles,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(rawSha256=sha(p),profiles=profiles)))
