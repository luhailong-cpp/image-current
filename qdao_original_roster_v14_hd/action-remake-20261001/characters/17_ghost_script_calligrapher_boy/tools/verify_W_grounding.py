from pathlib import Path
from PIL import Image
import hashlib, json
b=Path(__file__).resolve().parents[1]
r=json.loads((b/"review/grounding-W/review.json").read_text(encoding="utf-8"))
issues=[]
for f in r["frames"]:
    p=b/f["file"]
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    with Image.open(p) as im:
        size=list(im.size)
        alpha="A" in im.getbands() and im.getextrema()[-1][0]==0
    receipt=json.loads(p.with_suffix(".png.generation.json").read_text(encoding="utf-8-sig"))
    if actual!=f["sha256"]: issues.append([f["n"],"review SHA mismatch"])
    if actual!=receipt.get("sha256"): issues.append([f["n"],"receipt SHA mismatch"])
    if size!=f["native_size"] or min(size)<1024 or size[0]!=size[1]: issues.append([f["n"],"bad dimensions"])
    if not alpha: issues.append([f["n"],"no transparent alpha"])
    for suffix in (".request.json",):
        if not (b/"provenance"/(f["key"]+suffix)).exists(): issues.append([f["n"],"request missing"])
    if not (b/"prompts"/(f["key"]+".txt")).exists(): issues.append([f["n"],"prompt missing"])
report={"scope":"selected W candidates only; metadata check, not visual acceptance","selected":len(r["frames"]),"issues":issues,"nativeSizes":[1254,1254],"visualAccepted":False}
(b/"review/grounding-W/record-check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))

