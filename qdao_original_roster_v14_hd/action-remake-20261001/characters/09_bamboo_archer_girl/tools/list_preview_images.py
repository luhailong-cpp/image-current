from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
allpngs=[]
for p in sorted(ROOT.rglob("*.png")):
 if "runtime" not in p.parts:allpngs.append(p.relative_to(ROOT).as_posix())
print(json.dumps(allpngs,ensure_ascii=False,indent=2))

