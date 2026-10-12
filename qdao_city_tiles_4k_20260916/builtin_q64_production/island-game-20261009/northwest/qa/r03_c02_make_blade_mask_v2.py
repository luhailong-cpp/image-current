from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
Q=Z/"qa/r03_c02_blade_repair_mask_v2"
Q.mkdir(exist_ok=False)
old=Z/"qa/r03_c02_blade_repair_mask_v1/source_selection_mask.png"
m=np.array(Image.open(old).convert("L"))
# A straight hard source-selection boundary across the small displaced facet.
# This chooses original pixels at identical coordinates; it paints no art.
yy,xx=np.mgrid[730:880,585:645]
m[730:880,585:645]=np.where(yy < xx+180,255,0).astype(np.uint8)
Image.fromarray(m).save(Q/"source_selection_mask.png")
a=np.array(Image.open(Z/"guides/r03_c02_repair_blade_middle_a03.native-crop.png").convert("RGB"))
b=np.array(Image.open(Z/"native/r03_c02_repair_blade_middle_a03.png").convert("RGB"))
Image.fromarray(np.where(m[:,:,None]==255,b,a)).save(Q/"combined_native_crop.png")
def rec(p):return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
(Q/"mask_selection.json").write_text(json.dumps({"operation":"binary same-coordinate source selection with straight local facet transition","baseMask":rec(old),"mask":rec(Q/"source_selection_mask.png"),"localOverrideBox":[585,730,645,880],"selectionRule":"repair iff y < x + 180 within override; existing verified binary mask elsewhere","pixelSynthesis":False,"repairPixelCount":int((m==255).sum())},indent=2))
print(int((m==255).sum()))

