from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,re
BASE=Path(__file__).resolve().parents[2]
src=(BASE/"source"/"cast"/"E").resolve()
assert src==Path(r"D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan/source/cast/E").resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in range(1,17):
 r=json.loads((BASE/"records"/"cast"/"E"/f"{n:02d}.generation.json").read_text(encoding="utf-8"))
 p=BASE/r["file"];im=Image.open(p)
 assert sha(p)==r["sha256"] and im.size==(1024,1024) and im.mode=="RGBA"
 assert (BASE/r["prompt"]).exists() and (BASE/r["evidence"]["receipt"]).exists()
files=list(src.glob("*.png"))
deletedAt=datetime.now(timezone.utc).isoformat()
entries=[]
for p in files:
 assert p.resolve().is_relative_to(src)
 entries.append({"file":p.relative_to(BASE).as_posix(),"sha256":sha(p),"deleted":True,"reason":"Final 1024 RGBA runtime and source text/receipts/SHAs verified; native or repair input no longer required as delivered game asset."})
for f in (BASE/"records"/"cast"/"E").glob("*.generation.json"):
 data=json.loads(f.read_text(encoding="utf-8"))
 data["derivedFrom"]["deleted"]=True
 data["derivedFrom"]["deletedAt"]=deletedAt
 data["derivedFrom"]["cleanupRecord"]="qa/cast/E-cleanup.json"
 for ref in data.get("references",[]):
  p=Path(ref["path"])
  if p.resolve().is_relative_to(src):
   ref["deletedAfterExport"]=True
   ref["deletedAt"]=deletedAt
   ref["cleanupRecord"]="qa/cast/E-cleanup.json"
   stem=p.name
   match=re.fullmatch(r"(\d{2})\.(attempt\d+)\.edit-input\.png",stem)
   if match:ref["generationRecord"]=f"records/cast/E/{match[1]}.{match[2]}.generation.json"
   elif re.fullmatch(r"\d{2}\.png",stem):
    ref["generationRecord"]=f"records/cast/E/{stem[:2]}"+(".attempt1" if ref.get("pathHasSinceBeenUpdated") else "")+".generation.json"
 f.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
cleanup={"deletedAt":deletedAt,"scope":"source/cast/E/*.png only","finalRuntimeVerified":16,"deletedImageCount":len(entries),"files":entries,"hostGeneratedFilesDeleted":False,"externalIdentityOrStyleReferencesDeleted":False}
for p in files:p.unlink()
(BASE/"qa"/"cast"/"E-cleanup.json").write_text(json.dumps(cleanup,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"deleted":len(entries),"runtimeVerified":16,"remainingSourcePNGs":len(list(src.glob("*.png")))},ensure_ascii=False))

