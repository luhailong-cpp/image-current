from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
z=Path(__file__).resolve().parent
s='r05_c02_southwest_ground_join_a01';out=z/'qa'/f'{s}_union_mask_v1';out.mkdir()
info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
parts=[z/'qa'/f'{s}_{name}_mask_v1/source_selection_mask.png' for name in ('ground','foot')]
mask=np.logical_or.reduce([np.array(Image.open(p))==255 for p in parts])
target=z/'guides'/f'{s}.native-crop.png';repair=z/'native'/f'{s}.png'
a=np.array(Image.open(target).convert('RGB'));b=np.array(Image.open(repair).convert('RGB'));c=a.copy();c[mask]=b[mask]
assert not mask[1139:].any()
mp=out/'source_selection_mask.png';cp=out/'combined_native_crop.png';Image.fromarray(mask.astype('uint8')*255).save(mp);Image.fromarray(c).save(cp)
r=dict(operation='Boolean union of same-coordinate binary hard source masks',components=[info(p) for p in parts],target=info(target),repair=info(repair),mask=info(mp),combinedCrop=info(cp),repairPixelCount=int(mask.sum()),resizing=False,registration=False,feathering=False,colorCorrection=False,pixelSynthesis=False,south115Unchanged=True)
(out/'mask_selection.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))

