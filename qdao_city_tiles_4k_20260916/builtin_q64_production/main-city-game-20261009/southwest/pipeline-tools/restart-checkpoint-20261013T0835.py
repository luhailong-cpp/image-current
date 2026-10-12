import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
tiles=[];new=[];issues=[]
for r in range(9,17):
 for c in range(1,9):
  tile=f"r{r:02d}_c{c:02d}";td=B/tile;sel=read(td/"refinement/selection.json") if (td/"refinement/selection.json").exists() else {}
  occupied=[];missing=[]
  for pr in range(1,5):
   for pc in range(1,5):
    pid=f"p{pr:02d}_{pc:02d}";rp=td/sel.get(pid,f"native/{pid}.png.generation.json")
    if not rp.exists():missing.append(pid);continue
    d=read(rp);im=Path(d["file"])
    if not im.exists():issues.append({"file":str(im),"issue":"missing selected source"});continue
    assert d.get("nativePixelsPreserved") is True and d.get("resizedAfterGeneration") is False
    assert [d["width"],d["height"]]==[1254,1254]
    occupied.append(pid)
    if d.get("generatedAt","") >= "2026-10-13T08:28":
     assert sha(im)==d["sha256"]
     with Image.open(im) as image: assert image.size==(1254,1254)
     rec=Path(d["evidence"]["toolReceipt"]);assert sha(rec)==d["evidence"]["toolReceiptSha256"]
     new.append({"tile":tile,"patch":pid,"file":str(im),"sha256":d["sha256"],"record":str(rp),"receipt":str(rec),"sourcePixelsVerified":True,"formalAccepted":False})
  tiles.append({"tile":tile,"nativeSlots":len(occupied),"missing":missing,"formalAccepted":False})
logs=[]
for uid in ["01a13460-a02f-71c0-9842-ccf99b18dc26","01a13460-f242-7fd3-aa6b-da88e697de10","01a13461-4bfa-7ea2-ba83-e14e8aa09f34"]:
 paths=list(Path("C:/Users/luyua/.codex/sessions/2026/10/13").glob("*"+uid+"*"))
 for lp in paths:
  size=lp.stat().st_size
  with lp.open("rb") as f:
   f.seek(max(0,size-4*1024*1024));blob=f.read()
  lines=blob.splitlines()
  if size>len(blob):lines=lines[1:]
  hints=[];calls=[]
  for line in lines:
   try:d=json.loads(line)
   except Exception:continue
   p=d.get("payload",{})
   typ=p.get("type")
   if typ in ["function_call","custom_tool_call"]:
    name=p.get("name","");args=p.get("arguments",p.get("input",""))
    calls.append({"timestamp":d.get("timestamp"),"name":name,"argsHead":str(args)[:220]})
   elif typ in ["function_call_output","custom_tool_call_output"]:
    s=json.dumps(p,ensure_ascii=False)
    found=re.findall(r"as (C:.*?exec-[a-f0-9-]+\\\\.png) by default",s)
    if not found:
     found=re.findall(r"exec-[a-f0-9-]+\\.png",s)
    if found:hints.append({"timestamp":d.get("timestamp"),"imageNames":list(dict.fromkeys(found))})
  logs.append({"file":str(lp),"boundedTailBytes":len(blob),"recentImageEvidence":hints[-4:],"lastCalls":calls[-4:]})
counts={"selectedNativePatchCount":sum(t["nativeSlots"] for t in tiles),"complete4kCandidateCount":sum(t["nativeSlots"]==16 for t in tiles),"partialTileCount":sum(0<t["nativeSlots"]<16 for t in tiles),"untouchedTileCount":sum(t["nativeSlots"]==0 for t in tiles),"formalAcceptedCount":0,"internalPassed4kCount":0,"externalPassed4kCount":0}
counts["remainingCorePatchCount"]=1024-counts["selectedNativePatchCount"]
counts["missingFullTileCount"]=64-counts["complete4kCandidateCount"]
report={"recordedAtUtc":now,"scope":"Current selected spatial slots only. Prior unchanged source verification reused; new ingested records since this restart hash/dimension/receipt checked. Coverage is not acceptance.","counts":counts,"newSavedNative":new,"tiles":tiles,"issues":issues,"agentNetworkErrors":[{"worker":name,"error":"Fatal error: application network permission was revoked","source":"Actual collaboration final-status delivered in parent turn"} for name in ["sw_left_restart_20261013","sw_right_restart_20261013","sw_col5_restart_20261013"]],"rootLastSuccessfulImageSaved":True,"generationCallsNotRetriedAfterExplicitNetworkRevocation":True,"paidApiUsed":False,"gitMutated":False,"boundedRecoveryEvidence":logs,"rootNext":"r13_c06:p03_03; not prepared yet","agentNext":{"left":"r09_c04:p02_01","right":"r10_c08:p03_02","col5":"r15_c05:p02_01"},"objectiveComplete":False}
out=B/"pipeline-tools/restart-network-checkpoint-20261013T0835.json"
assert not out.exists()
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=read(B/"progress.json")
p.update(counts)
p.update({"updatedAtUtc":now,"status":"native_production_network_permission_blocked","productionInProgress":False,"generationStopped":True,"networkBlocked":True,"holdNewImageGeneration":True,"imageGenerationInFlight":False,"rootImageGenerationInFlight":False,"productionLines":0,"activeCoordinate":"r13_c06:p03_03","primaryNewTileNativeCount":10,"latestInterruptionCheckpoint":str(out),"countsSnapshotUtc":now,"countsSnapshot":str(out),"countsSnapshotMayHaveAdvanced":False,"nextStep":"Resume same included builtin route after app network permission is restored; first check latest prepared calls for actual returns. Do not bypass permission denial or repeat saved native outputs.","networkPermissionStatus":"Three active subagents reported explicit application network permission revoked. Root's last already-returned image saved; no further network retries after these errors."})
p["workerStatus"]={"reportedAtUtc":now,"activeWorkers":[],"productionLines":0,"failedWorkers":[x["worker"] for x in report["agentNetworkErrors"]],"source":"Actual collaboration failures, not image model or quality restriction."}
p["zoneDeliverySummary"]={"targetDeduplicatedTiles":64,"full16Native4kCandidates":counts["complete4kCandidateCount"],"formalAccepted":0,"internalCheckedPassed":0,"missingNativePatchCount":counts["remainingCorePatchCount"],"countsSnapshotUtc":now,"scope":"Native coverage not visual acceptance"}
(B/"progress.json").write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"checkpoint":str(out),"counts":counts,"newSaved":new,"issues":issues,"logs":logs},ensure_ascii=False,indent=2))

