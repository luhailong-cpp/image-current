from pathlib import Path
import json,hashlib
z=Path(__file__).resolve().parent
p=z/"right-current-selection-20261012.json"
d=json.loads(p.read_text(encoding="utf8"))
rec=lambda p:{"path":p.as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
t=d["tiles"]["r06_c04"];t["assembled4k"]=True;t["candidate"]=rec(z/"tiles/r06_c04_candidate-v1_4096.png");t["record"]=rec(z/"tiles/r06_c04_candidate-v1_4096.assembly.json");t["qaIndex"]=rec(z/"qa/assembly_r06_c04_candidate-v1_4096/qa_index.json");t["internalClosurePassed"]=False
p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf8")
print(json.dumps(rec(p)))

