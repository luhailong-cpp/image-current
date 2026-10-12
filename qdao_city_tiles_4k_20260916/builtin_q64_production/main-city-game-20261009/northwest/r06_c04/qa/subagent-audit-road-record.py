import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")/"r06_c04"
old="r06_c04-candidate-minimum-error-8b97cad693aa";new="r06_c04-candidate-minimum-error-a55e10de83f3"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
img=B/"candidate"/(new+".png")
assert sha(img)=="60632020fc4c93251b77edd38a1851403e5dca3c835e53873e6409153e84e994"
m=json.loads((B/"candidate"/(new+".assembly.json")).read_text(encoding="utf-8-sig"))
prior=B/"qa"/"subagent-audit-full-report-8b97cad693aa.json"
review=[]
for q in m["qa"]:
 p=Path(q["file"]);op=B/"qa"/old/p.name;nh,oh=sha(p),sha(op)
 assert nh==q["sha256"]
 review.append({"file":str(p),"sha256":nh,"cropLTRB":q["cropLTRB"],"rotationCCW90":q["rotationCCW90"],"nativePixelScale":1,"viewed":True,"verdict":"pass","reviewEvidence":"directly viewed latest crop in road repair audit" if nh!=oh else "current crop byte-identical to previously passed crop; inherited viewing evidence","previousReviewedFile":str(op),"previousSha256":oh})
changed=sum(x["sha256"]!=x["previousSha256"] for x in review)
assert len(review)==33 and changed==11
report={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"tile":"r06_c04","candidate":{"file":str(img),"sha256":sha(img)},"scope":"Internal native-pixel seam and junction QA following s02_04_road01 selection","verdict":"pass","seamSegmentsCovered":24,"junctionsCovered":9,"latestChangedCropsActuallyViewedCount":changed,"latestIdenticalCropsInheritingViewedEvidence":33-changed,"priorReview":{"file":str(prior),"sha256":sha(prior)},"findings":[],"comments":["All 11 changed crop PNGs were actually viewed at native pixel scale.","No new internal petal, branch, timber, roof or material discontinuity requiring repair found.","22 byte-identical crops inherit the earlier passed review."],"externalBandInterface":"Out of scope; being coordinated separately. This report does not accept the external road-band interface.","formalAccepted":False,"nativeArtModified":False,"reviewedFiles":review}
out=B/"qa"/"subagent-audit-road-report-a55e10de83f3.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"report":str(out),"verdict":"pass","changedActuallyViewed":changed,"inheritedIdentical":33-changed,"candidateSha":sha(img)},indent=2))

