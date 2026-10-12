from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");s="r05_c03_window_sill_repair_a01";Q=Z/"qa"/f"{s}_mask_v1"
old=np.array(Image.open(Z/"guides"/f"{s}.native-crop.png"));new=np.array(Image.open(Q/"combined_native_crop.png"));m=np.array(Image.open(Q/"source_selection_mask.png"));raw=np.array(Image.open(Z/"native"/f"{s}.png"))
assert np.array_equal(new[:115],old[:115]) and np.array_equal(new[:,:290],old[:,:290])
assert np.array_equal(new[m==0],old[m==0]) and np.array_equal(new[m==255],raw[m==255])
Image.fromarray(new).crop((250,115,500,350)).save(Q/"sill_repair_detail_100pct.png")
report=dict(status="native repair and binary mask ready for root to apply to latest tile",raw=str(Z/"native"/f"{s}.png"),rawSha256=hashlib.sha256((Z/"native"/f"{s}.png").read_bytes()).hexdigest(),input=str(Z/"guides"/f"{s}.input.json"),cropBox=[2650,0,3904,1254],mask=str(Q/"source_selection_mask.png"),combined=str(Q/"combined_native_crop.png"),selectedPixelCount=int(np.count_nonzero(m==255)),top115RowsUnchanged=True,columnLeftOfCropX290Unchanged=True,maskZeroPixelsUnchanged=True,selectedPixelsExactNativeSource=True,localVisualPassed=True,wholeTileApplied=False)
(Q/"handoff.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps(report,indent=2))

