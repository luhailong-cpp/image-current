from pathlib import Path
import json,hashlib,argparse
Z=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument("--previous",required=True);ap.add_argument("--operation",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
p=Path(a.previous);op=Path(a.operation);out=Path(a.output)
data=json.loads(p.read_text(encoding="utf8"));operation=json.loads(op.read_text(encoding="utf8"))
for output in operation["outputs"]:
 tile=next(t for t in data["tiles"] if t["tileId"]==output["tileId"])
 tile["image"]=output["image"]
 rec=Path(output["projectionRecordPath"])
 tile["record"]={"path":str(rec),"sha256":hashlib.sha256(rec.read_bytes()).hexdigest()}
with out.open("x",encoding="utf8") as f:json.dump(data,f,indent=2)
print(out)

