from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
B=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x",encoding="utf-8") as f:json.dump(d,f,ensure_ascii=False,indent=2)
now=datetime.now(timezone.utc).isoformat()
tag=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
qdir=B/"work-r06_c02"/"qa"/"r06_c02_s01_s03_v01"
review={"reviewedAtUtc":now,"nativeWholeReviewed":True,"qaScale":1,"cropsReviewed":["n-1","n-2","e-1","e-2"],"result":"not-selected-pending-east-overlap-repair","formalAccepted":False,"issues":[{"location":"native x approximately 1024, y0..500","issue":"Straight vertical ground-texture discontinuity between dense small pebbles and larger eastern stones; clear in east upper QA crop."},{"location":"east upper QA crop bottom, roof ridge transition","issue":"Ridge upper outline changes slope at current east join; targeted repair and recheck required."}],"note":"Original preserved. No propagation from this candidate. New generation unavailable after subagent permission-revocation errors; not counted as a failed repair attempt."}
write_new(qdir/"visual.pending-v1.json",review)
idx=read(B/"current-artifacts.json")
tiles={k:v for k,v in idx.items() if k.startswith("r") and isinstance(v,dict) and "candidate" in v}
assert len(tiles)==12
old=read(B/"progress.json")
snap=B/"production-checkpoints"/(tag+".json")
newids=["r06_c02_s01_s04_v01","r06_c02_s01_s04_v02","r06_c02_s01_s03_v01"]
outputs=[]
for ident in newids:
 p=B/"native"/(ident+".png");g=read(str(p)+".generation.json")
 assert sha(p)==g["sha256"]
 receipt=read(B/"work-r06_c02"/"receipts"/(ident+".receipt.json"))
 assert sha(receipt["originalFile"])==g["sha256"]
 outputs.append({"ident":ident,"file":str(p),"sha256":g["sha256"],"originalFile":receipt["originalFile"],"actualModel":None,"actualQuality":None,"selected":ident=="r06_c02_s01_s04_v02"})
pending={"r06_c02":{"selectedCores":1,"next":"Repair s01_s03_v01 east ground-texture boundary and inspect ridge, preserving s01_s04_v02; native outputs and receipts already saved."},"r02_c05":{"savedNativeFiles":len(list((B/"work-r02_c05/native").glob("*.png"))),"selectedCores":6,"pendingRequest":"r02_c05_s03_s03_v01","outputSaved":False},"r06_c03":{"selectedCores":len(list((B/"work-r06_c03/selections").glob("*.json"))),"note":"Worker failed before new response with application network permission revoked."},"r02_c02":{"selectedCores":16,"internalAccepted":False,"note":"Roof junction remains pending repair; consult latest versioned worker patch records; apply two-no-improvement deferral rule."}}
blocks=[{"agent":"sol_north","error":"Fatal error: application network permission was revoked"},{"agent":"sol_paving","error":"Fatal error: application network permission was revoked"},{"agent":"sol_e3","error":"Selected model is at capacity. Please try a different model."}]
write_new(snap,{"createdAtUtc":now,"status":"saved-local-checkpoint-external-runtime-block","userIntent":"Continue original NW production to completion","rootRule":"AGENTS.md","split":"docs/MAP_PARALLEL_SPLIT_20261013.json","reservedOverlapWithOwnedNW":False,"newOutputs":outputs,"activeWork":pending,"runtimeBlocks":blocks,"internalPassed4kCount":12,"target4kCount":49,"formalAcceptedCount":0,"fullyCovered4kCount":13,"fullyCoveredPendingRepairOrQaCount":1,"notes":["No paid API, no credential or permission changes, no shared Git mutations.","No retry of denied networking or agent restart after revocation.","Existing accepted QA reused; no historical image scan, overview rebuild or repackage."]})
write_new(B/"production-checkpoints"/(tag+".previous-progress.json"),old)
z=tiles["r06_c04"];qp=B/z["qa"];qa=read(qp)
assert qa["internalAccepted"] and sha(B/z["candidate"])==qa["candidate"]["sha256"]
old["currentCandidates"]["r06_c04"]={"candidate":z["candidate"],"candidateSha256":qa["candidate"]["sha256"],"internalAccepted":True,"qa":z["qa"],"qaSha256":sha(qp),"assembly":z["assembly"],"assemblySha256":sha(B/z["assembly"]),"formalAccepted":False}
old.update({"updatedAt":now,"status":"native-production-saved-external-runtime-block","currentTile":"r06_c02","currentPatch":"s01_s03_v01-east-join-pending-repair","complete4kCount":12,"candidate4kCount":12,"internalPassed4kCount":12,"missingInternalPassed4kCount":37,"fullyCoveredPendingRepairOrQaCount":1,"lastNewOutput":str(B/"native"/(newids[-1]+".png")),"currentCheckpoint":str(snap.relative_to(B)),"inFlightGeneration":False,"runtimeBlocks":blocks,"nativeCountsStatus":"Retained historical census; not refreshed by this minimal checkpoint. See newOutputs in checkpoint for this batch.","nextStep":"Resume existing work from saved outputs after runtime/network access is restored; no repeated generation of returned images."})
tmp=B/"progress.checkpoint-tmp.json"
tmp.write_text(json.dumps(old,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
tmp.replace(B/"progress.json")
print(json.dumps({"checkpoint":str(snap),"outputsSavedAndOriginalHashVerified":len(outputs),"internalPassed":12,"target":49,"activeWork":pending},ensure_ascii=False))

