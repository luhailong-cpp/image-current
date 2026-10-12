import json,hashlib
from pathlib import Path
Z=Path(__file__).resolve().parents[1]
matrix=[["01_01_a07","01_02_a02","01_03_a01","01_04_a01"],["02_01_a02","02_02_a02","02_03_a01","02_04_a01"],["03_01_a02","03_02_a02","03_03_a01","03_04_a01"],["04_01_a01","04_02_a01","04_03_a01","04_04_a01"]]
records=[]
for row in matrix:
 out=[]
 for suffix in row:
  p=Z/"native"/("r04_c04_s"+suffix+".png"); g=p.with_name(p.name+".generation.json")
  assert p.exists() and g.exists(),p
  out.append({"path":str(p),"generationRecord":str(g),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
 records.append(out)
m={"schemaVersion":1,"tileId":"r04_c04","nativePixels":1254,"corePixels":1024,"haloPixels":115,"patchMatrix":records,"status":"explicit_selection_for_candidate_assembly","note":"Native builtin pixels only; no final resizing. Requires internal and cross4k review."}
dest=Z/"qa/r04_c04_manifest_v1.json"
with dest.open("x",encoding="utf-8") as f:json.dump(m,f,ensure_ascii=False,indent=2)
print(str(dest))

