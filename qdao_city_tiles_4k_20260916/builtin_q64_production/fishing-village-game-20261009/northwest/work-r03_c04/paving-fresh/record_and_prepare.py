from pathlib import Path
from PIL import Image
import hashlib,json,re,shutil,datetime,sys
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest"); out=root/"work-r03_c04/paving-fresh"; name="r03_c04_paving_localshape_v01"
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
request=read(out/(name+".request.json")); receipt=read(out/(name+".receipt.json"))
original=Path(re.search(r" as (C:\\[^\n]+?\.png) by default",receipt["output_hint"]).group(1))
dst=out/(name+".png");shutil.copy2(original,dst)
im=Image.open(dst); assert im.size==(1254,1254)
record={"file":str(dst),"sha256":sha(dst),"generatedAt":receipt["returnedAt"],"width":im.width,"height":im.height,"format":"PNG","tool":"image_gen.imagegen","route":"builtin","nativeScaleResampled":False,"actualModel":None,"actualQuality":None,"submittedParameters":{"model":None,"quality":None},"unverifiedReason":"Built-in tool exposes no model or quality selector and returns no actual model/quality.","globalNativeBox":request["globalNativeBox"],"globalCoreBox":[12753,8727,13777,9751],"nativeCoreCropBox":[115,115,1139,1139],"configSnapshot":read(Path(r"D:/work/image/config/image-generation.json")),"evidence":{"receipt":str(out/(name+".receipt.json")),"request":str(out/(name+".request.json")),"returnedFields":receipt["resultKeys"]},"prompt":str(out/(name+".prompt.txt")),"references":[{"file":p,"sha256":sha(Path(p)),"role":role} for p,role in zip(request["referenced_image_paths"],request["referenceRoles"])],"toolOriginal":{"file":str(original),"sha256":sha(original)},"status":"native-pending-edge-QA"}
(out/(name+".png.generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
sys.path.insert(0,str(root/"work-r03_c04"))
from apply_r03_c04_repairs import overlay_mask
import numpy as np
target=np.asarray(Image.open(out/"junction-shape-target.png")).copy(); native=np.asarray(im)
mask,paths=overlay_mask(target,native)
target[mask]=native[mask]
Image.fromarray(target).save(out/"proposal-region.png")
Image.fromarray(mask.astype(np.uint8)*255).save(out/"proposal-mask.png")
(out/"proposal-paths.json").write_text(json.dumps(paths),encoding="utf-8")
print(json.dumps({"native":str(dst),"sha256":sha(dst),"selectedPixels":int(mask.sum())}))

