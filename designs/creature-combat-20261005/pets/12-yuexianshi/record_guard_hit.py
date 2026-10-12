import json, subprocess, sys, hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
n=int(sys.argv[1]); tag=sys.argv[2] if len(sys.argv)>2 else f"{n:02}.guardfix-20261008"
payload=json.loads((ROOT/"records"/"hit-W"/f"{tag}.receipt.json").read_text(encoding="utf-8"))
source=payload["source"]
refs=[]
roles=["original identity E","original true rear identity W","confirmed painted materials style","local edit target: current hit-W frame; lower-body repair only","only permitted baseline-W leg/shoe stance; derived from cast W16"]
for i,path in enumerate(payload["submittedParameters"]["referenced_image_paths"]):
    r={"path":path,"role":payload.get("referenceRoles",roles)[i]}
    if i>=3:r["historicalGenerationInput"]=True
    refs.append(r)
job={"action":"hit","direction":"W","index":n,"source":source,"generatedAt":payload["returnedAt"],"prompt":f"prompts/hit-W/{tag}.txt","receipt":f"records/hit-W/{tag}.receipt.json","references":refs,"visualStatus":"static-reviewed-guard-stance-repaired; dynamic-playback-not-verified"}
p=ROOT/"records"/"hit-W"/f"{tag}.job.json"
p.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding="utf-8")
native=ROOT/"records"/"hit-W"/f"{tag}.generation.json"
subprocess.run([sys.executable,str(ROOT/"record_native_candidate.py"),str(p),str(native)],check=True)
data=json.loads(native.read_text(encoding="utf-8"));data["disposition"]=payload.get("disposition","selected guard stance repair");native.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
if not payload.get("candidateOnly",False):subprocess.run([sys.executable,str(ROOT/"export_frame.py"),str(p)],check=True)

