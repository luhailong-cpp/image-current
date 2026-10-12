from pathlib import Path
from PIL import Image
import hashlib,json
b=Path(__file__).resolve().parents[1]
versions={n:2 if n in {1,3,5,7,9,10,12,13,15,16} else 1 for n in range(1,17)};versions[4]=3;versions[6]=3;versions[8]=3
rows=[]
for n,v in versions.items():
    p=b/"staging"/f"run-N-{n:02}-v{v}.png"
    with Image.open(p) as im:size=list(im.size);mode=im.mode;alpha=im.getchannel("A").getextrema() if "A" in im.getbands() else None
    rec=json.loads(p.with_suffix(".png.generation.json").read_text(encoding="utf-8-sig"))
    rows.append({"n":n,"file":str(p.relative_to(b)).replace(chr(92),"/"),"key":p.stem,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"native_size":size,"alpha_extrema":alpha,"receipt_sha256":rec.get("sha256"),"request_exists":(b/"provenance"/(p.stem+".request.json")).exists(),"prompt_exists":(b/"prompts"/(p.stem+".txt")).exists()})
(b/"review/phase-N"/"selected-records.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(rows,ensure_ascii=False))

