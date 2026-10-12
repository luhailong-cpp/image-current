import json
from pathlib import Path
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");w=b/"work-r04_c02";p=b/"native/r04_c02_s04_s02_v01.png";g=json.loads(Path(str(p)+".generation.json").read_text(encoding="utf-8-sig"))
(w/"selections/s04_s02.json").write_text(json.dumps({"file":str(p),"sha256":g["sha256"],"row":4,"column":2,"status":"selected-for-composition-repair-pending","visualQA":"qa/r04_c02_s04_s02_v01/visual.json"},indent=2),encoding="utf-8")
(w/"qa/r04_c02_s04_s02_v01/visual.json").write_text(json.dumps({"status":"pending-whole-rope-bridge","reviewed":["n-1.100pct.png","n-2.100pct.png","e-1.100pct.png","e-2.100pct.png"],"notes":"North native overlaps continuous. East lower suspension rope is visibly severed/stepped; upper rope direction changes. Need complete native bridge across global x~6030..6260, y~15600..16450. Not pass."},indent=2),encoding="utf-8")
