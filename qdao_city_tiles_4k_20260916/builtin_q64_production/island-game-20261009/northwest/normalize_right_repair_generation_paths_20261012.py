from pathlib import Path
import json,hashlib
z=Path(__file__).resolve().parent
for stem in ["r06_c04_paving_material_east_a01","r06_c04_paving_material_east_a02","r06_c04_center_grout_a01","r06_c04_center_grout_a02"]:
 p=z/"native"/f"{stem}.png.generation.json"
 d=json.loads(p.read_text(encoding="utf8"));old=d["prompt"];q=z/old
 assert hashlib.sha256(q.read_bytes()).hexdigest()==d["promptSha256"]
 d["prompt"]=q.as_posix()
 d["pathNormalizationEvidence"]={"originalRecord":{"path":p.as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()},"originalPromptValue":old,"reason":"cwd-relative ingest prompt resolves same hash-identical file; immutable corrected sibling","artModified":False}
 out=z/"native"/f"{stem}.png.generation-pathfixed-v1.json"
 with out.open("x",encoding="utf8") as f:json.dump(d,f,indent=2)
 print(out.as_posix())

