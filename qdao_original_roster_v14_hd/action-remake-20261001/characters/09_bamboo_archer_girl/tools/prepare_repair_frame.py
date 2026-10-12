import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
spec=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
a,d,f=spec["action"],spec["direction"],int(spec["frame"])
slot=f"{a}-{d}-{f:02d}"
stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
out=ROOT/"provenance"/("run-"+d if a=="run" else "combat-"+d)/(slot+"-repair-"+stamp+".request.json")
out.parent.mkdir(exist_ok=True)
args={"prompt":spec["prompt"],"referenced_image_paths":spec["references"],"transparent_background":True}
request={"slot":slot,"action":a,"direction":d,"frame":f,"requestedAt":datetime.now(timezone.utc).isoformat(),"configSnapshot":json.loads((ROOT.parents[3]/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,**args},"referenceMetadata":[{"path":p,"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest(),"role":"edit_target" if i==0 else "pose_or_approved_style"} for i,p in enumerate(spec["references"])],"repairReason":spec.get("reason")}
out.write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"request":str(out),"args":args,"action":a,"direction":d,"frame":f},ensure_ascii=False))

