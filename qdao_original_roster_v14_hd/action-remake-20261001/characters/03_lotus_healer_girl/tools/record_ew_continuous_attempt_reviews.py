from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parent.parent
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
notes=load(B/"review/ew-continuous-attempt-notes.json")["notes"]
rows=[]
for stem,note in notes.items():
 p=B/"generation"/(stem+".png")
 if not p.exists(): continue
 rec=load(str(p)+".generation.json")
 row={"file":str(p.relative_to(B)).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"native":rec["native"],"alphaGt8Bounds":rec["alphaGt8Bounds"],"prompt":rec["prompt"],"promptSha256":rec["promptSha256"],"references":rec["references"],"receipt":rec["evidence"]["receipt"],"actualModel":None,"actualQuality":None,"reviewedAt":datetime.now(timezone.utc).isoformat(),"review":note,"visualAccepted":False,"clientAccepted":False,"alignmentApplied":False}
 rows.append(row)
 out=B/"review"/("continuous-attempt-"+stem.replace("/","-")+".json")
 out.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"review/ew-continuous-attempts.json").write_text(json.dumps({"schemaVersion":1,"attemptCount":len(rows),"note":"Technical provenance and honest static observations. Text target coordinates are not measured outcome or acceptance. Earlier/raw receipt gaps explicitly documented.","attempts":rows},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"attemptCount":len(rows),"filesComplete":all((B/r["prompt"]).exists() and (B/r["receipt"]).exists() for r in rows)}))
