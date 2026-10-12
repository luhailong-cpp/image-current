from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest')
s='r03_c04_repair_paving_lower_a01'
out=Z/'qa'/f'{s}_union_mask-v1'
out.mkdir(exist_ok=False)
paths=[Z/'qa'/f'{s}_{k}_mask-v1'/'source_selection_mask.png' for k in ('upper','lower')]
ms=[np.array(Image.open(p))==255 for p in paths]
assert not (ms[0]&ms[1]).any()
mask=ms[0]|ms[1]
old=np.array(Image.open(Z/'guides'/f'{s}.native-crop.png').convert('RGB'))
new=np.array(Image.open(Z/'native'/f'{s}.png').convert('RGB'))
combined=old.copy();combined[mask]=new[mask]
assert not mask[-44:].any()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=out/'source_selection_mask.png';cp=out/'combined_native_crop.png'
Image.fromarray(mask.astype('uint8')*255).save(mp);Image.fromarray(combined).save(cp)
record=dict(operation='binary union of disjoint native masks',resizing=False,feathering=False,colorCorrection=False,pixelSynthesis=False,sourceMasks=[dict(path=p.as_posix(),sha256=sha(p)) for p in paths],mask=dict(path=mp.as_posix(),sha256=sha(mp)),combined=dict(path=cp.as_posix(),sha256=sha(cp)),repairPixelCount=int(mask.sum()),bottom44RowsUnchanged=True)
(out/'union_record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))

