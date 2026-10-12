import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest");q=z/"r06_c05/qa";folder=q/"s02_01_material02_fix04";ev=json.loads((folder/"mechanical-evidence.json").read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(ev["candidate"])==ev["candidateSha256"]
entries=[]
for e in ev["entries"]:
 assert sha(e["file"])==e["sha256"]
 for src in e["sources"]:assert sha(src["file"])==src["sha256"]
 entries.append({**e,"verdict":"passed","actuallyViewed":True,"inheritedFrom":None,"findings":[{"description":"Mid-road grout now changes shade gradually with no abrupt endpoint at native x230; tiny red paper is a whole irregular diamond, not a clipped triangle."}] if e["name"]=="west" else []})
for name in ["joint-and-paper","midgrout"]:
 p=folder/(name+".png")
 entries.append({"name":name,"file":str(p),"sha256":sha(p),"verdict":"passed","actuallyViewed":True,"inheritedFrom":None,"findings":[]})
r={"schemaVersion":2,"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewer":"finish_material_review","candidate":ev["candidate"],"candidateSha256":ev["candidateSha256"],"candidateActuallyViewed":True,"nativePixels":[1254,1254],"summary":{"nativeCandidateViewed":1,"fourEdgePairsViewed":4,"focusedDetailsViewed":2,"blocking":0,"result":"passed local native review"},"entries":entries,"fixedDefects":[{"region":[0,456,401,467],"description":"Middle road grout stays continuous; native x229->231 minimum row brightness changes from 124->13 in fix01 to 113->112.7 in fix04, then gradually darkens toward x400. Numerical values support, not substitute for, native visual inspection."},{"region":[218,577,245,600],"description":"Small red paper now has both left and right halves and complete irregular diamond silhouette."}],"provenance":{"tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"sourceUnmodifiedToolOutput":True,"layoutGuideUsedAsReferenceOnly":str(z/"r06_c05/layout-only/s02_01_material02_fix04.microrepair-guide.png"),"guideDerivation":str(z/"r06_c05/layout-only/s02_01_material02_fix04.microrepair-guide.png.derivation.json")},"supersedesLocalReview":str(q/"s02_01_material02_fix01-review-20261011.json"),"correctionRecord":str(q/"s02_01_material02_fix01-review-correction-20261011.json"),"sourceSelection":"approved for next joint assembly; whole joint delta QA pending","formalAccepted":False,"qualification":"One source and local pairs only; not an acceptance of the whole tile, region or map."}
op=q/"s02_01_material02_fix04-review-20261011.json"
if op.exists():raise FileExistsError(op)
op.write_text(json.dumps(r,indent=2),encoding="utf-8")
reject={"candidate":str(z/"r06_c05/native/s02_01_material02_fix03.png"),"sha256":"f42c753d5f28397e1ef835b5d9b14d82558c61b5da79963790ffa9133a775ad0","verdict":"rejected","reason":"Tiny paper remained clipped and x230 grout transition was insufficiently corrected. Native source and pairs viewed; not selected.","nextCandidate":ev["candidate"]}
(q/"s02_01_material02_fix03-rejected.json").write_text(json.dumps(reject,indent=2),encoding="utf-8")
print(json.dumps({"report":str(op),"sha256":sha(op)}))

