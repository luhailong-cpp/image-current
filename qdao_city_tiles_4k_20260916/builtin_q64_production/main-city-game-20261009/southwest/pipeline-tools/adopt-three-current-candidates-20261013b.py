from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
repair=B/"r13_c06/repairs-resume-20261012/stair-V3-full-native-v01"
rp=repair/"qa-native/root-review.json";assert not rp.exists()
review={"reviewedAtUtc":now,"assembly":str(repair/"integrated/assembly.json"),"actualNativeCropAndFourBoundariesViewed":True,"sourceResampling":False,"targetDefect":"repeated stair edge height jumps at V3","localGeometryImproved":True,"targetJoinVisualPassed":True,"repairOuterEdges":"Viewed top/bottom/left/right native panels; no remaining gross edge phase jumps in repaired stair faces. Fine wood/stone tone changes need final material QA.","internalWholeTilePassed":False,"formalAccepted":False,"remainingIssues":["Roof phase defects remain unchanged","Left neighbor geometry fronts remain","Stone cellular texture and lantern/gold/post approved-geometry comparisons remain"]}
rp.write_text(json.dumps(review,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
items=[("r13_c06",repair/"integrated/assembly.json",rp),("r09_c04",B/"r09_c04/pipeline/output/214a45bdb9b55d2b/assembly.json",B/"r09_c04/pipeline/qa/recover20261013-v01/actual-review-and-repair-queue.json"),("r10_c08",B/"r10_c08/pipeline/output/72f40489f8fbeac8/assembly.json",B/"r10_c08/pipeline/qa/72f40489f8fbeac8/recover-review-v01/visual-review.json")]
catalog=read(B/"current-candidates.json")
for tile,ap,qa in items:
 a=read(ap);assert a["tile"]==tile and a["verifiedNativeCount"]==16
 for e in [a["output"],a["contextOutput"]]:
  assert sha(e["file"])==e["sha256"]
  with Image.open(e["file"]) as im:assert im.size==((4096,4096) if e==a["output"] else (4326,4326))
 assert qa.exists()
 catalog["tiles"][tile]={"tile":tile,"source":"native-current-reviewed-candidate","assembly":str(ap),"assemblySha256":sha(ap),"candidate":a["output"],"context":a["contextOutput"],"coreWorldBox":a["selectedCoreWorldBox"],"verifiedNativeSlots":16,"sourceResampling":False,"internalPassed":False,"externalPassed":False,"formalAccepted":False,"visualReview":str(qa),"visualReviewSha256":sha(qa)}
catalog["updatedAtUtc"]=now
(B/"current-candidates.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
ts=[]
for r in range(9,17):
 for c in range(1,9):
  tile=f"r{r:02d}_c{c:02d}";td=B/tile;sel=read(td/"refinement/selection.json") if (td/"refinement/selection.json").exists() else {};n=0;missing=[]
  for pr in range(1,5):
   for pc in range(1,5):
    pid=f"p{pr:02d}_{pc:02d}";record=td/sel.get(pid,f"native/{pid}.png.generation.json")
    if not record.exists():missing.append(pid);continue
    d=read(record);assert Path(d["file"]).is_file() and [d["width"],d["height"]]==[1254,1254] and d["nativePixelsPreserved"] and not d["resizedAfterGeneration"];n+=1
  ts.append({"tile":tile,"selectedNativeSlots":n,"missing":missing,"candidateRegistered":tile in catalog["tiles"],"formalAccepted":False})
counts={"selectedNativePatchCount":sum(t["selectedNativeSlots"] for t in ts),"fullyCovered4kCount":sum(t["selectedNativeSlots"]==16 for t in ts),"complete4kCandidateCount":len(catalog["tiles"]),"partialTileCount":sum(0<t["selectedNativeSlots"]<16 for t in ts),"untouchedTileCount":sum(t["selectedNativeSlots"]==0 for t in ts),"remainingCorePatchCount":1024-sum(t["selectedNativeSlots"] for t in ts),"formalAcceptedCount":0,"internalPassed4kCount":0,"externalPassed4kCount":0}
counts["missingFullTileCount"]=64-counts["fullyCovered4kCount"]
snapshot=B/"pipeline-tools/current-slot-counts-20261013b.json";assert not snapshot.exists()
snapshot.write_text(json.dumps({"snapshotUtc":now,"scope":"Only current unique selected spatial slots, no historical version scans. Prior unchanged source checks reused; three newly adopted full candidates hashed/dimension verified. Source coverage differs from acceptance.","counts":counts,"tiles":ts,"newCandidateAssemblies":[str(x[1]) for x in items],"formalAccepted":0},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=read(B/"progress.json");p.update(counts);p.update(updatedAtUtc=now,countsSnapshotUtc=now,countsSnapshot=str(snapshot),countsSnapshotMayHaveAdvanced=True,status="native_production_in_progress",productionInProgress=True,generationStopped=False,networkBlocked=False,holdNewImageGeneration=False,productionLines=4,activeCoordinate="r14_c06:p01_01",primaryNewTile="r14_c06",activeTile="r14_c06")
p["zoneDeliverySummary"]={"targetDeduplicatedTiles":64,"full16Native4kCandidates":counts["fullyCovered4kCount"],"internalCheckedPassed":0,"formalAccepted":0,"missingNativePatchCount":counts["remainingCorePatchCount"],"countsSnapshotUtc":now}
p["workerStatus"]={"reportedAtUtc":now,"activeGenerationWorkers":["root","sw_left_recover_20261013b","sw_right_recover_20261013b","sw_col5_recover_20261013b"],"productionLines":4,"source":"Root and original three internal lanes resumed from actual on-disk outputs.","activeGenerationTiles":["r14_c06","r10_c01","r11_c07","r16_c05"]}
(B/"progress.json").write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"counts":counts,"catalogEntries":len(catalog["tiles"]),"snapshot":str(snapshot)},ensure_ascii=False))

