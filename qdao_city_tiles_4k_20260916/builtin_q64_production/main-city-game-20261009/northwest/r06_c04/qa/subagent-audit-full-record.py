import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")/"r06_c04"
old="r06_c04-candidate-minimum-error-fe8edb4d2939";new="r06_c04-candidate-minimum-error-8b97cad693aa"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
img=B/"candidate"/(new+".png")
assert sha(img)=="27059dbc0121a7c23f47b22b4683f707e4a2bb3986ca7ea650d47a6e59ccd313"
m=json.loads((B/"candidate"/(new+".assembly.json")).read_text(encoding="utf-8-sig"))
review=[]
for q in m["qa"]:
 p=Path(q["file"]);op=B/"qa"/old/p.name
 nh,oh=sha(p),sha(op)
 assert nh==q["sha256"]
 review.append({"file":str(p),"sha256":nh,"cropLTRB":q["cropLTRB"],"rotationCCW90":q["rotationCCW90"],"nativePixelScale":1,"viewed":True,"verdict":"pass","reviewEvidence":"directly viewed latest crop" if nh!=oh else "old crop directly viewed; current file byte-identical SHA-256","previousReviewedFile":str(op),"previousSha256":oh})
assert len(review)==33
changed=sum(x["sha256"]!=x["previousSha256"] for x in review)
report={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"tile":"r06_c04","candidate":{"file":str(img),"sha256":sha(img)},"scope":"Internal native-pixel seam and junction visual QA only","verdict":"pass","seamSegmentsCovered":24,"junctionsCovered":9,"previousCandidateActuallyViewedCount":33,"latestChangedCropsActuallyViewedCount":changed,"latestIdenticalCropsInheritingViewedEvidence":33-changed,"totalViewImageInspectionsThisFullAudit":33+changed,"findings":[],"resolved":[{"finding":"Two vertical gold trim lines on flag ended abruptly at row join","previousCandidate":old,"previousPatch":"s04_04","replacementPatch":"s04_04_fix01","latestStatus":"resolved; no gold-line stubs in latest internal-y3072-segment04.png; nearby flower/leaf junction and cloth texture visually continuous"}],"comments":["All 24 seam segments and 9 junctions are covered at native pixel scale.","No actionable broken tree branch, chopped blossom, disconnected eave/tile line, lantern rib jump or abrupt internal material boundary found in latest covered crops.","Replacing s04_04 altered 10 QA PNGs because the horizontal minimum-error path can change beyond the changed patch; all 10 were re-viewed, rather than assuming only three changed."],"externalSeams":"Not accepted by this report. Existing separate external north-boundary findings remain in subagent-audit-report.json.","formalAccepted":False,"nativeArtModified":False,"reviewedFiles":review}
out=B/"qa"/"subagent-audit-full-report-8b97cad693aa.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"report":str(out),"verdict":report["verdict"],"covered":len(review),"reViewed":changed,"inheritedIdentical":33-changed,"candidateSha":sha(img)},indent=2))

