from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[2]
rec=BASE/"records"/"cast"/"E"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in rec.glob("*.generation.json"):
 data=json.loads(f.read_text(encoding="utf-8"))
 is_history=".attempt" in f.name
 n=int(f.name[:2])
 if is_history:
  data["artifactStatus"]="superseded/rejected; old project runtime and native source replaced; text provenance retained"
  data["supersededBy"]=f"records/cast/E/{n:02d}.generation.json"
  data["runtimeReplaced"]=True
  data["derivedFrom"]["deleted"]=True
  data["derivedFrom"]["deletedReason"]="This attempted source at the recorded project path was replaced by a subsequent accepted AI result. Its generated host output receipt remains evidence; no host file deletion was performed."
 else:
  data["visualStatus"]="all final E frames individually inspected and contact sheet inspected; sequence playback pending"
  data["visualInspection"]="qa/cast/E-visual-review.md"
 for ref in data.get("references",[]):
  p=Path(ref["path"])
  # Historical generation steps referred to previous source versions before targeted repairs.
  if is_history and n in [10,11,12] and p.as_posix().endswith(f"source/cast/E/{n-1:02d}.png"):
   stored=BASE/"source"/"cast"/"E"/f"{n-1:02d}.attempt1.edit-input.png"
   if stored.exists():
    ref["sha256AtGeneration"]=sha(stored)
    ref["historicalInputCopy"]=stored.relative_to(BASE).as_posix()
    ref["pathHasSinceBeenUpdated"]=True
    continue
  if p.exists():ref["sha256AtGeneration"]=sha(p)
 f.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("Updated final and superseded provenance records with current or historical reference SHA.")

