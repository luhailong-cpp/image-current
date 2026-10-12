from pathlib import Path
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
d=json.loads((B/"review-run-NE.json").read_text(encoding="utf-8"))
assert len(d["frames"])==16 and d["missingSlots"]==[]
assert len(set(x["slot"] for x in d["frames"]))==16
for f in d["frames"]:
 assert hashlib.sha256(Path(f["file"]).read_bytes()).hexdigest()==f["sha256"]
new=["09-v3","09-v4","10-v1","12-v1","14-v1","15-v1","16-v1","16-v2","16-v3","04-v2","07-v2","08-v2","07-v3","08-v3"]
missing=[]
for suffix in new:
 key="run-NE-"+suffix
 for p in [B/"provenance"/(key+".request.json"),B/"provenance"/(key+".tool-result.json"),B/"staging"/(key+".png.generation.json")]:
  if not p.exists():missing.append(p.as_posix())
for key in ["cast-E-10-v6","cast-E-10-v7"]:
 for p in [B/"provenance"/(key+".request.json"),B/"provenance"/(key+".tool-result.json"),B/"staging"/(key+".png.generation.json")]:
  if not p.exists():missing.append(p.as_posix())
print(json.dumps(dict(selectedHashCheck="16/16",timing=d["timing"],provenanceMissing=missing,expectedNewRecords=16)))

