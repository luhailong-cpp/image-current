from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");s="r05_c03_paving_tip_repair_a01";Q=Z/"qa"/f"{s}_mask_v1"
old=np.array(Image.open(Z/"guides"/f"{s}.native-crop.png"));new=np.array(Image.open(Q/"combined_native_crop.png"));m=np.array(Image.open(Q/"source_selection_mask.png"));raw=np.array(Image.open(Z/"native"/f"{s}.png"))
assert np.array_equal(new[m==0],old[m==0]) and np.array_equal(new[m==255],raw[m==255])
for sl in (np.s_[0],np.s_[-1],np.s_[:,0],np.s_[:,-1]):assert np.array_equal(new[sl],old[sl])
Image.fromarray(new).crop((100,420,400,650)).save(Q/"tip_repair_detail_100pct.png")
report=dict(status="native raw plus mask ready for root latest tile",raw=str(Z/"native"/f"{s}.png"),input=str(Z/"guides"/f"{s}.input.json"),baseVersion="r05_c03_candidate-v6_4096",cropBox=[2700,2700,3954,3954],mask=str(Q/"source_selection_mask.png"),combined=str(Q/"combined_native_crop.png"),selectedPixelCount=int(np.count_nonzero(m==255)),allOuterEdgesUnchanged=True,maskZeroPixelsUnchanged=True,selectedPixelsExactNativeSource=True,localVisualPassed=True,wholeTileApplied=False)
with (Q/"handoff.json").open("x",encoding="utf8") as f:json.dump(report,f,indent=2)

