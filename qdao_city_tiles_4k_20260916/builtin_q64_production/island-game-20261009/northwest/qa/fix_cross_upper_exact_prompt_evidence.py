from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");s="cross_r03_c03c04_paving_upper_a01"
old=Z/"receipts"/f"{s}.receipt.json";r=json.loads(old.read_text(encoding="utf8"))
p=Z/"prompts"/f"{s}.exact.prompt.txt"
with p.open("x",encoding="utf8",newline="") as f:f.write(r["submitted"]["promptText"])
r["submitted"]["promptFile"]=p.as_posix();r["evidenceCorrection"]="Exact submitted prompt restored without editor-added trailing newline; no generation repeated."
receipt=Z/"receipts"/f"{s}.exact-prompt.receipt.json"
with receipt.open("x",encoding="utf8") as f:json.dump(r,f,indent=2)
gp=Z/"native"/f"{s}.png.generation.json";g=json.loads(gp.read_text(encoding="utf8"))
g["prompt"]=p.as_posix();g["promptSha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
g["evidence"]["receipt"]=receipt.as_posix()
g["evidenceCorrection"]={"reason":"Saved prompt file had an added trailing newline. The exact actual submitted prompt is preserved from original receipt.","supersedesRecord":{"path":gp.as_posix(),"sha256":hashlib.sha256(gp.read_bytes()).hexdigest()},"rawImageChanged":False,"generationRepeated":False}
new=Z/"native"/f"{s}.png.generation-evidence-v2.json"
with new.open("x",encoding="utf8") as f:json.dump(g,f,indent=2)
print(new)

