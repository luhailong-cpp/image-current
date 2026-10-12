from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c10"); d=t/"qa/local-repair-20261013"
src=Path(r"C:/Users/luyua/.codex/generated_images/01a13556-d78f-7763-b993-330ab85ba156/exec-75841aa3-0906-4300-83f1-d9bd196df4c4.png"); dst=t/"native/cloud-upper-local-v20261013.png"; assert not dst.exists()
with Image.open(src) as im: assert im.size==(1254,1254)
shutil.copy2(src,dst)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt={"tool":"image_gen","route":"builtin","status":"success","savedAt":datetime.now(timezone.utc).isoformat(),"sourceOutputPath":str(src),"sourceOutputSha256":sha(src),"workspaceFile":str(dst),"sha256":sha(dst),"actualModel":None,"actualQuality":None,"nativePixels":[1254,1254],"sourceKept":True}
(t/"receipts/cloud-upper-local-v20261013.receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
Path(str(dst)+".generation.json").write_text(json.dumps(receipt,indent=2)+"\n")
base=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c10/qa/core-baseline/aa79b145eff57b69aabf/r08_c10-core-baseline.candidate.png"); im=Image.open(base).convert("RGB")
local=(59,395,1139,800); origin=(1421,397)
im.paste(Image.open(dst).convert("RGB").crop(local),(origin[0]+local[0],origin[1]+local[1]))
out=d/"r08_c10-local-v1.candidate.png"; assert not out.exists(); im.save(out)
m={"sourceCandidate":str(base),"sourceSha256":sha(base),"nativeRepair":str(dst),"nativeSha256":sha(dst),"sourceCrop":list(local),"destination":[1480,792],"candidate":str(out),"candidateSha256":sha(out),"operation":"integer crop paste only; no feather/rescale","internalPassed":False,"remainingDefect":"Horizontal paving joint cuts at y1024; first attempt removed isolated blue stripe"}
(d/"r08_c10-local-v1.json").write_text(json.dumps(m,indent=2)+"\n")
tar=d/"cloud-upper-target-v2.png";im.crop((1421,397,2675,1651)).save(tar)
print(json.dumps(m))

