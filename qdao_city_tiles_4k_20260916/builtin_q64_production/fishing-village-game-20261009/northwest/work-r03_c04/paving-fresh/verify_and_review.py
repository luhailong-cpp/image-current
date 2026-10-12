from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest"); out=root/"work-r03_c04/paving-fresh"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
resolve=lambda x: Path(x) if Path(x).is_absolute() else root/x
manifest=out/"r03_c04.paving-proposal-v1.assembly.json"; r=json.loads(manifest.read_text(encoding="utf-8"))
pixels=np.asarray(Image.open(r["candidate"]["file"])); ids=np.asarray(Image.open(r["sourceIdMap"]["file"]))
assert sha(r["candidate"]["file"])==r["candidate"]["sha256"]
assert sha(r["sourceIdMap"]["file"])==r["sourceIdMap"]["sha256"]
checked=[]
for source in r["sources"]:
 p=resolve(source["file"]);assert sha(p)==source["sha256"];gp=resolve(source["generationRecord"]);assert sha(gp)==source["generationRecordSha256"]
 sr=np.asarray(Image.open(p));yy,xx=np.nonzero(ids==source["sourceId"]);x,y,_,_=source["nativeBox"]
 assert np.all((yy-y>=0)&(yy-y<1254)&(xx-x>=0)&(xx-x<1254))
 mismatch=int(np.count_nonzero(np.any(pixels[yy,xx]!=sr[yy-y,xx-x],axis=1)))
 assert mismatch==0;checked.append({"sourceId":source["sourceId"],"pixels":int(len(yy)),"mismatches":mismatch})
assert sum(v["pixels"] for v in checked)==4096**2
base=np.asarray(Image.open(r["base"]["candidate"]));mask=np.asarray(Image.open(r["overlays"][0]["maskFile"]))>0
unmodified=pixels.copy();unmodified[420:1674,350:1604][mask]=base[420:1674,350:1604][mask]
assert np.array_equal(unmodified,base)
proof={"verifiedAt":datetime.now(timezone.utc).isoformat(),"manifest":{"file":str(manifest),"sha256":sha(manifest)},"sources":checked,"verifiedPixels":4096**2,"mismatchedPixels":0,"outsideActualMaskUnchanged":True,"noResampling":True,"noFeather":True,"noPixelColorRewrite":True}
(out/"provenance-replay.json").write_text(json.dumps(proof,indent=2),encoding="utf-8")
qa={"reviewedAt":datetime.now(timezone.utc).isoformat(),"candidate":r["candidate"],"assemblyRecord":str(manifest),"assemblyRecordSha256":sha(manifest),"repairAccepted":True,"internalPavingBlockingCleared":True,"formalAccepted":False,"scope":"Only r03_c04 internal paving repair; independent south/west boundary work remains owned by other agents.","nativeBox":[350,420,1604,1674],"globalNativeBox":[12638,8612,13892,9866],"actualContributionMask":r["overlays"][0]["maskFile"],"maskSha256":r["overlays"][0]["maskSha256"],"selectedPixels":r["overlays"][0]["selectedPixels"],"inspectionScale":1,"inspection":[{"artifact":x,"accepted":True,"finding":("Continuous original neighboring slab contours across hard ownership edge; no doubled strip, broken corner, new lighting line, or scale change." if x["name"] in ["north","south","west","east"] else "Original truncated bevel replaced with a complete stone boundary. Lower-right intentionally retains the irregular staggered T-junction and unequal slab footprints; no detached thin fragment.")} for x in r["qaCrops"]],"newSource":{"file":r["sources"][-1]["file"],"sha256":r["sources"][-1]["sha256"],"generationRecord":r["sources"][-1]["generationRecord"],"generationRecordSha256":r["sources"][-1]["generationRecordSha256"],"sourceIdInProposal":r["sources"][-1]["sourceId"]},"integration":{"method":"Paste generated native pixels only wherever saved mask is 255, at tile offset [350,420]. Remap sourceId by native file identity when merging with independent south boundary proposal.","baseCropUnchangedRequirement":"Parent must confirm incoming base at this tile box still equals original r03_c04.candidate.png, or re-QA resulting four edges.","otherBoundariesUnchanged":True},"rejectedExplorations":{"test01Through04":"Existing bridge v01-v04 with relaxed interior DP caused repeated narrow stones or displaced corners and are excluded from proposal.","newNativeCalls":1},"mechanicalProof":str(out/"provenance-replay.json"),"notes":["All sources remain native1254 pixels; final4096 pixels independently replayed.","All new reference paths were viewed and actually submitted.","Model and quality actual values are null; no paid API."]}
(out/"paving-repair-review.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"repairAccepted":True,"candidate":r["candidate"],"assemblyRecordSha256":sha(manifest),"QA":str(out/"paving-repair-review.json"),"qaSha256":sha(out/"paving-repair-review.json"),"pixelsVerified":4096**2,"sources":len(checked)}))

