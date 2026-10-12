from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c10");d=t/"qa/local-repair-20261013";now=datetime.now(timezone.utc).isoformat()
src=Path(r"C:/Users/luyua/.codex/generated_images/01a13556-d78f-7763-b993-330ab85ba156/exec-5d06df7f-b024-41a2-82d3-40a0b491c406.png")
dst=t/"native/cloud-upper-local-v20261013-v2.png";assert not dst.exists()
with Image.open(src) as im:assert im.size==(1254,1254)
shutil.copy2(src,dst);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={"tool":"image_gen","route":"builtin","status":"success","savedAt":now,"sourceOutputPath":str(src),"sourceOutputSha256":sha(src),"workspaceFile":str(dst),"sha256":sha(dst),"actualModel":None,"actualQuality":None,"nativePixels":[1254,1254],"sourceKept":True}
(t/"receipts/cloud-upper-local-v20261013-v2.receipt.json").write_text(json.dumps(r,indent=2)+"\n")
Path(str(dst)+".generation.json").write_text(json.dumps(r,indent=2)+"\n")
report={"tile":"r08_c10","updatedAt":now,"status":"native_16_complete_internal_QA_pending","selectedCoreCount":16,"completeCandidateCount":1,"internalPassed4kCount":0,"formalAcceptedCount":0,"baselineManifest":str(t/"qa/core-baseline/aa79b145eff57b69aabf/assembly.json"),"candidate":str(d/"r08_c10-local-v1.candidate.png"),"candidateSha256":sha(d/"r08_c10-local-v1.candidate.png"),"nativeRepairCount":2,"localRepairResult":{"blueStripe":"Removed in selected local-v1","horizontalCut":"Second output improves central crossing but shifts adjacent slab joints; not adopted until bounded composition validated","attempts":2,"status":"P2 retained; proceed independent missing tiles after bounded attempts"},"remainingP2":[{"id":"row1-row2-paving-cuts","coordinate":"tile y1024, across p11/p21,p12/p22,p13/p23","status":"pending"},{"id":"p22-p23-cloud-close","coordinate":"tile x2048, central cloud scroll lower closure","status":"pending"},{"id":"p33-p34-stone-joints","coordinate":"tile x3072, y2048..3072","status":"pending"},{"id":"p43-p44-stone-joints","coordinate":"tile x3072, y3072..4096","status":"pending"}],"reusedPreviousReview":str(t/"qa/model-requirement-pause-20261012/visual-review.json"),"externalSeams":"pending current neighboring sources","nextTile":"r08_c09","route":"builtin","actualModel":None}
(d/"review-checkpoint-20261013.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
p=json.loads((t/"tile-progress.json").read_text());p.update({"updatedAt":now,"status":report["status"],"candidate":report["candidate"],"candidateSha256":report["candidateSha256"],"nativeCount":len(list((t/"native").glob("*.png"))),"completeCandidateCount":1,"internalPassed4kCount":0,"generationStopped":False,"blocker":None,"inflightGeneration":None,"unsavedSuccessfulOutputs":0,"visualReview":str(d/"review-checkpoint-20261013.json"),"partialAssemblyManifest":report["baselineManifest"],"nextStep":"Bounded local repair retains P2. Advance independent r08_c09 from stable r08_c10 west edge."})
(t/"tile-progress.json").write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"selectedCandidate":p["candidate"],"sha256":p["candidateSha256"],"internalPassed":0,"nativeCount":p["nativeCount"]}))

