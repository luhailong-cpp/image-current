from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((ROOT/"inventory-run-north.json").read_text(encoding="utf-8-sig"))
rows=[]
for row in inv["frames"]:
 p=ROOT/row["native_evidence"];rec=json.loads(p.read_text(encoding="utf-8-sig"));native=ROOT/rec["native"]["file"];host=Path(rec.get("evidence",{}).get("hostOutput",""))
 if host.is_file() and native.is_file() and sha(host)!=sha(native):
  rows.append({"slot":row["path"],"record":str(p),"native":str(native),"host":str(host),"nativeSha":sha(native),"hostSha":sha(host)})
print(json.dumps(rows,ensure_ascii=False,indent=2))
(ROOT/"work/run-NW/import-collisions-20261003.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")

