from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
s="r06_c03_paving_natural_lower_a01"
prior=Z/"qa/r06_c03_paving_natural_lower_mask_v1"
out=Z/"qa/r06_c03_paving_natural_lower_mask_v2"
assert not out.exists();out.mkdir()
old=np.asarray(Image.open(Z/f"guides/{s}.native-crop.png").convert("RGB"))
new=np.asarray(Image.open(Z/f"native/{s}.png").convert("RGB"))
m=np.asarray(Image.open(prior/"source_selection_mask.png"))==255
polys=[
[(0,140),(378,140),(378,433),(346,430),(332,484),(275,453),(237,423),(214,379),(165,365),(144,349),(109,359),(92,325),(0,290)],
[(696,430),(1138,292),(1138,369),(696,512)],
[(736,651),(1138,510),(1138,1254),(1080,1254),(1078,1148),(1019,1082),(988,1015),(939,991),(884,949),(875,902),(833,847),(813,779),(763,713)]
]
allowed=Image.new("L",(1254,1254),0);d=ImageDraw.Draw(allowed)
for p in polys:d.polygon(p,fill=255)
sel=m & (np.asarray(allowed)==255)
joined=old.copy();joined[sel]=new[sel]
assert np.array_equal(joined[~sel],old[~sel]) and np.array_equal(joined[sel],new[sel])
mp=out/"source_selection_mask.png";cp=out/"combined_native_crop.png"
Image.fromarray(sel.astype(np.uint8)*255).save(mp);Image.fromarray(joined).save(cp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
rec={"operation":"same-coordinate hard source selection restricted to three pavement exposure polygons","pixelSynthesis":False,"resizing":False,"feathering":False,"colorCorrection":False,"target":info(Z/f"guides/{s}.native-crop.png"),"repair":info(Z/f"native/{s}.png"),"priorMinimumErrorMask":info(prior/"source_selection_mask.png"),"restrictionPolygons":polys,"mask":info(mp),"combinedCrop":info(cp),"repairPixelCount":int(sel.sum()),"retainedTargetPixelCount":int((~sel).sum()),"purpose":"Keep carved pillar and rails plus the large foliage field unchanged. Polygons select only visible pavement; exact same-coordinate pixels from one of two native sources.","visualStatus":"pending"}
(out/"mask_selection.json").write_text(json.dumps(rec,indent=2)+"\n",encoding="utf8")
print(json.dumps({"output":info(cp),"selected":int(sel.sum())}))

