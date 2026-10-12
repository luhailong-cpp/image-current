from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def rec(p):return {"path":p.as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
out=Z/"right-current-selection-20261012.json"
if out.exists(): data=json.loads(out.read_text(encoding="utf8"))
else:data={"schemaVersion":1,"agent":"/root/right_completion","resumeAuthorization":rec(Path("D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json")),"historicalFreezePreserved":rec(Z/"qa/right-migration-freeze-20261011.json"),"tiles":{"r06_c04":{"matrix":[["a01","a03","a02","a01"],["a01",None,None,None],[None,None,None,None],[None,None,None,None]],"assembled4k":False,"internalClosurePassed":False,"formalAccepted":False,"knownPendingRepair":"Western stone railing blind/stepped courses need whole-object correction; do not count provisional native as accepted."},"r07_c04":{"matrix":[[None]*4 for _ in range(4)],"assembled4k":False,"internalClosurePassed":False,"formalAccepted":False}}}
for stem in sys.argv[1:]:
    parts=stem.split("_");tile="_".join(parts[:2]);r=int(parts[2][1:])-1;c=int(parts[3])-1
    assert (Z/"native"/(stem+".png")).is_file()
    data["tiles"][tile]["matrix"][r][c]=parts[4]
for tile,t in data["tiles"].items():
    t["cells"]=[]
    for r,row in enumerate(t["matrix"],1):
        for c,a in enumerate(row,1):
            if a is None:continue
            stem=f"{tile}_s{r:02d}_{c:02d}_{a}"
            p=Z/"native"/(stem+".png");gp=p.with_suffix(".png.generation.json")
            g=json.loads(gp.read_text(encoding="utf8"));assert g["sha256"]==rec(p)["sha256"]
            t["cells"].append({"stem":stem,"image":rec(p),"generationRecord":rec(gp),"receipt":rec(Z/"receipts"/(stem+".receipt.json")),"selection":"provisional_pending_internal_QA"})
    t["selectedCount"]=len(t["cells"]);t["requiredCount"]=16
data["updatedAtUtc"]=datetime.now(timezone.utc).isoformat()
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"path":out.as_posix(),"sha256":rec(out)["sha256"],"counts":{k:v["selectedCount"] for k,v in data["tiles"].items()}}))

