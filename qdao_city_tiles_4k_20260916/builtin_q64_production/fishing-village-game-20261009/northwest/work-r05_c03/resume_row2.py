from pathlib import Path
import json
from datetime import datetime,timezone
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");w=b/"work-r05_c03";old=json.loads((w/"receipts/r05_c03_s02_s01_v01.request.json").read_text())
ident="r05_c03_s02_s01_v02";old["promptFile"]=str(w/"prompts"/(ident+".prompt.txt"));old["referenced_image_paths"][3]=r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg"
old["globalNativeBox"]=[8077,17293,9331,18547];old["globalCoreBox"]=[8192,17408,9216,18432]
old["supersedesFailedAttempt"]="r05_c03_s02_s01_v01: failed before output due to unavailable reference; no native image generated"
old["createdAt"]=datetime.now(timezone.utc).isoformat()
Path(old["promptFile"]).write_text(old["prompt"],encoding="utf-8")
(w/"receipts"/(ident+".request.json")).write_text(json.dumps(old,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
progress=json.loads((w/"progress.json").read_text());progress.update(status="native-production-resumed",inFlight=True,currentPatch=ident,next="Complete second row from existing north native context, then remaining rows")
(w/"progress.json").write_text(json.dumps(progress,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(old))

