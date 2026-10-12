from pathlib import Path
import json,hashlib,argparse
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument("--version",type=int,required=True);a=a.parse_args()
p=z/"right-current-selection-20261012.json";d=json.loads(p.read_text(encoding="utf8"));t=d["tiles"]["r06_c04"]
rec=lambda q:{"path":q.as_posix(),"sha256":hashlib.sha256(q.read_bytes()).hexdigest()}
tile=z/f"tiles/r06_c04_candidate-v{a.version}_4096.png";prov=tile.with_suffix(".native-repair.json")
t.setdefault("priorCandidates",[])
if t.get("candidate") and t["candidate"]["path"]!=tile.as_posix():
 t["priorCandidates"].append({"candidate":t["candidate"],"record":t["record"]})
t["candidate"]=rec(tile);t["record"]=rec(prov);t["assembled4k"]=True;t["internalClosurePassed"]=False;t["formalAccepted"]=False
t["qaIndexScope"]="v1 baseline independent33QA; current repair boundary reviews pending, not closure"
t["repairStatus"]="in_progress; central/east row3 main grout joined, remaining lower boundary endpoints plus other v1 QA findings; cross-west rail deferred for unified neighbor baseline"
d["updatedAt"]=datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf8")
print(json.dumps(rec(p)))

