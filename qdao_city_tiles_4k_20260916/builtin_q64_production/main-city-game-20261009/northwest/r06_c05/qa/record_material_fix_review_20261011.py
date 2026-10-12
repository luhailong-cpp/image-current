import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")
p=z/"r06_c05/qa/s02_01-material02-fix01-audit.json"
a=json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(a["candidate"])==a["sha256"]
findings={
"west": "Muted blue-gray road meets the west neighbor without the prior jagged light-color patch; boundary and grout remain continuous. Subtle stone texture variation is nonblocking.",
"east": "Blue stone color and road borders meet the east neighbor continuously; no artificial rectangular or jagged tone band. Tiny texture variation is nonblocking.",
"north": "Upper slab chamfer and grout remain whole and connected. A faint texture-density transition is nonblocking.",
"south": "Leaf silhouettes and diagonal paver edges stay continuous with no visible cut-through leaf or orphan grout."
}
for e in a["entries"]:
 assert sha(e["file"])==e["sha256"]
 assert sha(e["sourceNeighbor"])==e["neighborSha256"]
 e.update(verdict="passed",actuallyViewed=True,inheritedFrom=None,findings=[findings[e["edge"]]])
a.update(reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer="finish_material_review",candidateActuallyViewed=True,summary={"nativeCandidateViewed":1,"nativePairsActuallyViewed":8,"inherited":0,"blocking":0,"result":"passed local four-edge review"},sourceSelection="approved for current joint assembly",formalAccepted=False,externalSeamsStatus="Final 8192 joint assembly delta QA pending",newArtGeneratedDuringReview=False,notes=["All 8 pair crops and the full 1254x1254 source were viewed at native pixel scale.","Prefer existing minimum-error cuts for this patch. No new cut override requested.","MAE measurements are diagnostic only and were not used as a rejection threshold.","This report accepts one selected source and its local pair crops, not the entire tile, region, or map."])
out=z/"r06_c05/qa/s02_01_material02_fix01-review-20261011.json"
if out.exists(): raise FileExistsError(out)
out.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"report":str(out),"sha256":sha(out),"candidateSha256":a["sha256"]}))

