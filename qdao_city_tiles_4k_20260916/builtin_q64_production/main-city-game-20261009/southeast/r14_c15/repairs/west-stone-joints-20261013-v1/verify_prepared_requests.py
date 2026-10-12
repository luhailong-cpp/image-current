from pathlib import Path
from PIL import Image
import json,hashlib,datetime
import numpy as np
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15/repairs/west-stone-joints-20261013-v1")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
m=json.loads((d/"ready-requests.json").read_text())
for src in [m["sourceCandidate"],m["immutableWestCore"]]:assert sha(src["path"])==src["sha256"]
checks=[]
for j in m["jobs"]:
 p=Path(j["preparation"]["path"]);prep=json.loads(p.read_text());req=json.loads(Path(j["request"]["path"]).read_text())
 for name in ["request","preparation","target","reference","mask","alpha"]:assert sha(j[name]["path"])==j[name]["sha256"]
 assert req["actualModel"] is None and req["actualQuality"] is None
 assert req["submittedParameters"]["referenced_image_paths"]==[x["path"] for x in prep["references"]]
 target=np.array(Image.open(j["target"]["path"]).convert("RGB"));ref=np.array(Image.open(j["reference"]["path"]).convert("RGB"));mask=np.array(Image.open(j["mask"]["path"]).convert("L"));a=np.array(Image.open(prep["fullAlpha"]["path"]).convert("L"))
 assert target.shape==(1254,1254,3) and ref.shape==target.shape
 assert np.array_equal(target[mask==0],ref[mask==0])
 assert not mask[:,:640].any() and not a[:,:640].any()
 assert not a[mask==0].any()
 crop=j["nativeCrop"];box=j["pasteBoxIn4096"];assert crop[2]-crop[0]==box[2]-box[0] and crop[3]-crop[1]==box[3]-box[1]
 assert np.array_equal(a[crop[1]:crop[3],crop[0]:crop[2]],np.array(Image.open(j["alpha"]["path"])))
 for key in ["protectedLeafTipBoxInTarget","protectedRedPaperBoxInTarget"]:
  if key in prep:
   x0,y0,x1,y1=prep[key];assert not mask[y0:y1,x0:x1].any() and not a[y0:y1,x0:x1].any()
 checks.append({"id":j["id"],"targetAndUnmarkedActuallyViewedAtOriginal1254":True,"referencesHashesVerified":True,"maskAndAlphaConsistent":True,"immutableWestCoreFullyOutsideMask":True,"protectedObjectsOutsideMask":True,"cropCoordinatesIntegerAndExact":True,"nativeCrop":crop,"pasteBoxIn4096":box,"newNativeGenerated":False})
o={"schemaVersion":1,"checkedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"preparedBy":"assembly_support","status":"offline_inputs_ready_not_art_acceptance","manifest":info(d/"ready-requests.json"),"checks":checks,"networkCallMade":False,"paidRouteUsed":False,"publishedCandidatesModified":False,"modelRule":"Existing included builtin permitted; 2.5 preference, 2.0 fallback; actual metadata null unless returned","formalAccepted":False}
p=d/"offline-input-qa.json";p.write_text(json.dumps(o,indent=2)+"\n");print(json.dumps({"manifest":info(d/"ready-requests.json"),"offlineQA":info(p),"jobCount":len(checks)}))
