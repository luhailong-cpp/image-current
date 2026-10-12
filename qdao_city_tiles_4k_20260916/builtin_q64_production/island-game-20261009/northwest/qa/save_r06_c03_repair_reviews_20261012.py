from pathlib import Path
from PIL import Image
import hashlib,json,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
def save(p,d):
 assert not p.exists()
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return info(p)
roof=[]
for folder,note in [
("r06_c03_roof_notch_mask_v1","Red fascia notch removed; gold curl and red lower edge complete, adjacent blue tile arc rims and shadow joints coherent."),
("r06_c03_south_bluejoin_mask_v2","Full blue-tile sequence is connected down to the south crop edge. Right boundary retains continuous red fascia; no clipped red edge. Rejected v1 not used.")
]:
 d=Z/"qa"/folder
 roof.append({"combined":info(d/"combined_native_crop.png"),"mask":info(d/"source_selection_mask.png"),"status":"pass","method":"connected_closure independently viewed the entire 1254 native image using view_image detail=original","notes":note})
print(save(Z/"qa/r06_c03_v3_roof_repairs_independent_review_20261012.json",{"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"pass_local_repairs","reviewer":"connected_closure","items":roof,"wholeTileAcceptance":False}))
for folder,note in [
("r06_c03_paving_natural_left_mask_v1","Large rectangular patches replaced with irregular mineral clouding and fine cracks; primary slab edges, moss nodes and bevel highlights remain continuous. Fine granularity remains compatible with the prior left material anchor."),
("r06_c03_paving_natural_right_mask_v1","Both thick grout blind ends reconnected; ball finial rendered with crisp painted stone detail. No new rectangular material cut edge or broken major slab contour.")
]:
 d=Z/"qa"/folder
 print(save(d/"visual_review.json",{"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"pass_local_selected_repair_pending_tile_closure","combined":info(d/"combined_native_crop.png"),"mask":info(d/"source_selection_mask.png"),"selectedPixels":json.loads((d/"mask_selection.json").read_text())["repairPixelCount"],"reviewers":[{"agent":"connected_closure","method":"Complete 1254 crop viewed at original resolution","result":"pass","notes":note},{"agent":"root","method":"Independent complete native 1254 visual inspection reported by collaboration message","result":"pass","notes":note}],"pending":"Rightmost 115 old stone pattern / local upper-rail soft focus intentionally reserved for cross-tile railing and material repair; north115 preserved for next group connection. Whole tile not yet accepted."}))
b=Z/"tiles/r06_c03_candidate-v5_4096.png";assert sha(b)=="259651b013fff85f79110270a9cac3fa2f3236d7b6d54e2b452c3b031a319068"
out=Z/"qa/r06_c03_v5_extra_20261012";out.mkdir(exist_ok=False)
p=out/"left_paving_lower_crop_boundary_100pct.png";box=[1750,900,3004,2154];Image.open(b).crop(box).save(p)
save(out/"index.json",{"base":info(b),"crops":[{**info(p),"tileCropBox":box,"nativeScale100Percent":True,"resizing":False}],"status":"pending_visual"})
print(info(p))

