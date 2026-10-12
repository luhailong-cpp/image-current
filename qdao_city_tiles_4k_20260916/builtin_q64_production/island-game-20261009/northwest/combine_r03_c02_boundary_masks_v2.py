from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(__file__).resolve().parent
q=Z/'qa/r03_c02_paving_boundary_union_mask_v2';q.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[Z/'qa'/p/'source_selection_mask.png' for p in ['r03_c02_paving_boundary_top_mask_v1','r03_c02_paving_boundary_mid_mask_v2','r03_c02_paving_boundary_low_mask_v1']]
m=np.zeros((1254,1254),bool)
for p in paths:m|=np.array(Image.open(p))==255
t=Z/'guides/r03_c02_repair_paving_boundary_a01.native-crop.png';r=Z/'native/r03_c02_repair_paving_boundary_a01.png'
a=np.array(Image.open(t).convert('RGB'));b=np.array(Image.open(r).convert('RGB'));a[m]=b[m]
mp=q/'source_selection_mask.png';cp=q/'combined_native_crop.png'
Image.fromarray(m.astype(np.uint8)*255).save(mp);Image.fromarray(a).save(cp)
rec={'operation':'Boolean union of native same-coordinate binary source selection masks','components':[{'path':p.as_posix(),'sha256':sha(p)} for p in paths],'target':{'path':t.as_posix(),'sha256':sha(t)},'repair':{'path':r.as_posix(),'sha256':sha(r)},'mask':{'path':mp.as_posix(),'sha256':sha(mp)},'combinedCrop':{'path':cp.as_posix(),'sha256':sha(cp)},'repairPixelCount':int(m.sum()),'resizing':False,'registration':False,'feathering':False,'pixelSynthesis':False}
(q/'mask_selection.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
print(json.dumps(rec))
