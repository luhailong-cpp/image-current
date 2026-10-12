from pathlib import Path
from PIL import Image
import json, hashlib, datetime
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/group-a-geometry/G07-worker")
root.mkdir(parents=True, exist_ok=True)
base=root.parents[5]
contract=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/production-contract.json")
c=json.loads(contract.read_text(encoding="utf-8-sig"))
target=root.parent/"input/group-a-target.native1254.png"
prompt="Use case: precise-object-edit.\nImage 1 is the EXACT edit target, a 1254 x 1254 native game-art paving crop. Return exactly 1254 x 1254 with identical crop, camera, scale, lighting, texture and topology. Images 2, 3, 4 are approved layout/material/art-style references only; do not copy their composition or introduce objects.\n\nPerform ONE extremely small repair: the stair-step notch in the existing upward-right diagonal grout around target pixel (533,365). This is the long diagonal from the left edge to the upper Y-junction. Its two existing portions are about 15 pixels laterally misregistered. Repair only a short local transition near x=480..595, y=325..410 so that the dark grout channel and both pale bevel lips become a single uninterrupted smooth continuous joint. Accommodate the small mismatch with a subtle local bend/taper; retain both original distant segments exactly at their existing pixel positions. DO NOT translate, straighten, reangle, redraw, normalize, or shift the whole diagonal.\n\nPreserve these observed original anchors and their surroundings: (420,439), (450,418), (480,396), then the right-hand segment at (575,347), (595,334) and onward. The existing notch lies between the local left anchors (495,386),(515,372) and right anchors (535,374),(555,361). These are source groove positions, not new positions. Ease only this tiny transition from one existing side to the other. The left T-junction near (420,439), upper Y-junction near (914,112), all outer edge pixels, all other grooves and all material must remain unchanged.\n\nDo not repair either unrelated dangling seam in the lower half. Keep the lower large crossing near (837,1095), dangling tip near (533,810), short dangling branch near (718,1171), and every other paving feature exactly where it already is. No broad material repaint, no geometric grid cleanup, no additional grout, no new objects, no text or markings. Output the original scene with only the tiny upper diagonal notch smoothed."
refs=[str(target),c["layoutReference"],c["detailStyleReference"],c["primaryStyleReference"]]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
prompt_path=root/"G07-v1.prompt.txt"
prompt_path.write_text(prompt,encoding="utf-8")
req={"id":"G07-v1","intent":"precise-object-edit","prompt":prompt,"promptPath":str(prompt_path),"promptSha256":sha(prompt_path),"referenced_image_paths":refs,"inputs":[{"path":p,"sha256":sha(p),"role":"edit target" if i==0 else "approved style reference","size":list(Image.open(p).size)} for i,p in enumerate(refs)],"expectedNativeSize":[1254,1254],"actualModel":None,"actualQuality":None,"attemptLimit":1,"contextCropBox":[512,2100,1766,3354],"coreOrigin":[397,1985],"createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat()}
(root/"request.json").write_text(json.dumps(req,indent=2),encoding="utf-8")
print(json.dumps(req))

