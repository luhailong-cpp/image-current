import sys,json,hashlib
from pathlib import Path
root=Path("D:/work/image")
expected={"AGENTS.md":"57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a","docs/MAP_PARALLEL_SPLIT_20261013.json":"a7cab49b89974586a1a0375baeadc5d4a7aa12dce6e782bcc8f9b52b777b3c8f"}
checks=[]
for name,digest in expected.items():
 data=(root/name).read_bytes()
 text=data.decode("utf-8-sig")
 actual=hashlib.sha256(data).hexdigest()
 if actual!=digest:
  print(text);sys.exit(2)
 checks.append({"path":name,"sha256":actual,"readCurrentContents":True,"matchesRulesAlreadyRead":True})
split=json.loads((root/"docs/MAP_PARALLEL_SPLIT_20261013.json").read_text(encoding="utf-8-sig"))
excluded=[t for b in split["batches"] if b["map"]=="fishing-village-game-20261009" and b["owner"]=="01a1216d-3f65-7331-939e-0ea73b19f3bf" and b["status"]=="allocated_root_reserved" for t in b["tiles"]]
if len(sys.argv)>1:assert sys.argv[1] not in excluded
print(json.dumps({"checks":checks,"excludedTiles":excluded}))
