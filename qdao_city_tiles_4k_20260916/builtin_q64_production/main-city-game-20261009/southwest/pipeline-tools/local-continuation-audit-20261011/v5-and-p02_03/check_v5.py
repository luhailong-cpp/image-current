import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image
from datetime import datetime,timezone
O=Path(__file__).parent;S=O.parents[2];I=S/"integrated-20261011"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
arr=lambda p:np.array(Image.open(p).convert("RGB"))
patches=[]
for version in [3,4,5]:
 assembly=read(I/f"v{version}/assembly.json")
 for patch in assembly["patches"]:
  pp=patch["patchEvidence"];mm=patch["maskEvidence"]
  patches.append({"version":version,"id":patch["id"],"worldBox":patch["worldBox"],"data":arr(pp["file"]),"mask":np.array(Image.open(mm["file"]).convert("L"))>0,"patchSha256":sha(pp["file"]),"maskSha256":sha(mm["file"]),"evidenceHashesMatch":sha(pp["file"])==pp["sha256"] and sha(mm["file"])==mm["sha256"]})
v5=read(I/"v5/assembly.json");tiles=[]
for tile,x in v5["outputs"].items():
 source=read(I/"v2/assembly.json")["outputs"][tile];core=x["coreWorldBox"];context=[core[0]-115,core[1]-115,core[2]+115,core[3]+115]
 old=arr(source["context"]["file"]);expected=old.copy();appliedmask=np.zeros(old.shape[:2],bool);applications=[]
 for p in patches:
  wx,wy,wr,wb=p["worldBox"];l,t,r,b=max(context[0],wx),max(context[1],wy),min(context[2],wr),min(context[3],wb)
  if l>=r or t>=b:continue
  mc=p["mask"][t-wy:b-wy,l-wx:r-wx];pc=p["data"][t-wy:b-wy,l-wx:r-wx];target=expected[t-context[1]:b-context[1],l-context[0]:r-context[0]]
  target[mc]=pc[mc];appliedmask[t-context[1]:b-context[1],l-context[0]:r-context[0]]|=mc
  applications.append({"version":p["version"],"id":p["id"],"maskPixelsInContext":int(mc.sum())})
 new=arr(x["candidate"]["file"]);ctx=arr(x["context"]["file"])
 d=np.any(ctx!=old,axis=2);basecore=old[115:4211,115:4211];cored=np.any(new!=basecore,axis=2)
 edgechanges={side:int(region.sum()) for side,region in [("north",cored[:1]),("south",cored[-1:]),("west",cored[:,:1]),("east",cored[:,-1:])]}
 tiles.append({"tile":tile,"candidate":x["candidate"],"context":x["context"],"declaredHashesMatch":sha(x["candidate"]["file"])==x["candidate"]["sha256"] and sha(x["context"]["file"])==x["context"]["sha256"],"expectedContextReplayFromV2Exact":bool(np.array_equal(expected,ctx)),"coreEqualsContextCrop":bool(np.array_equal(new,ctx[115:4211,115:4211])),"outsideAllAddedMasksChangedPixels":int(d[~appliedmask].sum()),"changedCorePixelsFromV2":int(cored.sum()),"changedContextPixelsFromV2":int(d.sum()),"onePixelBoundaryChangeCountsFromV2":edgechanges,"applications":applications})
segments=[]
for p in sorted((I/"v5/qa").glob("*segment*.png")):
 prior=I/"v2/qa"/p.name
 segments.append({"file":str(p),"pixels":list(Image.open(p).size),"sha256":sha(p),"pixelIdenticalToV2":bool(np.array_equal(arr(p),arr(prior))) if prior.exists() else None,"resized":False})
out={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"resume_crossedge_audit","status":"mechanical_replay_pass_with_remaining_visual_issues","assembly":{"file":str(I/"v5/assembly.json"),"sha256":sha(I/"v5/assembly.json")},"tileChecks":tiles,"patchSequence":[{k:v for k,v in p.items() if k not in ["data","mask"]} for p in patches],"nativeSegments":segments,"pendingVisualReviewOfChangedSegments":[x["file"] for x in segments if not x["pixelIdenticalToV2"]],"sourceArtworkModified":False,"formalAcceptedCount":0}
(O/"v5-mechanical-evidence.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"tiles":tiles,"changedSegments":[x["file"] for x in segments if not x["pixelIdenticalToV2"]]},ensure_ascii=False))

