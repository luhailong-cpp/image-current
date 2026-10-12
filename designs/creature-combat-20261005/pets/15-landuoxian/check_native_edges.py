from pathlib import Path
from PIL import Image
import json,numpy as np
R=Path(__file__).resolve().parent
for f in json.loads((R/'manifest.json').read_text(encoding='utf-8'))['frames']:
 r=json.loads((R/f['generationRecord']).read_text(encoding='utf-8-sig'))
 d=r['derivedFrom'];p=Path(d.get('file') or d.get('nativeFile'));p=p if p.is_absolute() else R/p
 if not p.exists():continue
 a=np.array(Image.open(p).getchannel('A'))
 edges=[int((a[0,:]>128).sum()),int((a[-1,:]>128).sum()),int((a[:,0]>128).sum()),int((a[:,-1]>128).sum())]
 if max(edges)>8:print(f['file'],edges)
