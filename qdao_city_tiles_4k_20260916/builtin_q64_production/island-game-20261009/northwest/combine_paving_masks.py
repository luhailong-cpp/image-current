from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=Z/'qa/repair_paving_a01_union_mask-v1';q.mkdir(exist_ok=False)
mps=[Z/'qa'/f'repair_paving_a01_node{i}_mask-v1/source_selection_mask.png' for i in (1,2)]
arrays=[np.array(Image.open(p))==255 for p in mps]
assert not (arrays[0]&arrays[1]).any();m=arrays[0]|arrays[1]
target=Z/'guides/r03_c03_repair_paving_a01.native-crop.png';raw=Z/'native/r03_c03_repair_paving_a01.png'
a=np.array(Image.open(target).convert('RGB'));b=np.array(Image.open(raw).convert('RGB'));c=a.copy();c[m]=b[m]
mp=q/'source_selection_mask.png';cp=q/'combined_native_crop.png'
Image.fromarray(m.astype(np.uint8)*255).save(mp);Image.fromarray(c).save(cp)
rec=dict(operation='disjoint Boolean union of two hard same-coordinate source-selection masks',components=[dict(path=p.as_posix(),sha256=sha(p)) for p in mps],target=dict(path=target.as_posix(),sha256=sha(target)),repair=dict(path=raw.as_posix(),sha256=sha(raw)),mask=dict(path=mp.as_posix(),sha256=sha(mp)),repairPixelCount=int(m.sum()),resizing=False,registration=False,feathering=False,colorCorrection=False)
(q/'mask_selection.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rec))
