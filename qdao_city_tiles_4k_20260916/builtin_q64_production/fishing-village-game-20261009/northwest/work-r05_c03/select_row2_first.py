import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");w=b/"work-r05_c03";f=b/"native/r05_c03_s02_s01_v02.png"
r={"file":str(f),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"row":2,"column":1,"status":"selected-pending-full-tile-QA"}
(w/"selections/s02_s01.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
qa={"reviewedAt":datetime.now(timezone.utc).isoformat(),"native":r,"dimensions":[1254,1254],"northPairAccepted":True,"inspectedAt100Percent":["s02s01-north-v02-segment1.png","s02s01-north-v02-segment2.png"],"findings":"Continuous cream rope and blue net borders; no missing knot or hard horizontal material strip. Native lower rear net hems complete, front net continues beyond crop.","formalAccepted":False}
(w/"qa/r05_c03_s02_s01_v02.visual-qa.json").write_text(json.dumps(qa,indent=2)+"\n",encoding="utf-8")
progress=json.loads((w/"progress.json").read_text());progress.update(generationOutputs=8,selectedCandidateFragments=5,inFlight=False,currentPatch="r05_c03_s02_s02_v01",next="Continue row2 east from selected s02s01");(w/"progress.json").write_text(json.dumps(progress,indent=2)+"\n",encoding="utf-8")

