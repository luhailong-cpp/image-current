from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];out=Z/"qa/r04_c04_v4_native_review"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tile=Z/"tiles/r04_c04_candidate-v4_4096.png";record=Z/"tiles/r04_c04_candidate-v4_4096.native-repair.json"
base=np.array(Image.open(Z/"tiles/r04_c04_candidate-v1_4096.png"));latest=np.array(Image.open(tile))
edge={"top":bool(np.array_equal(base[0],latest[0])),"bottom":bool(np.array_equal(base[-1],latest[-1])),"left":bool(np.array_equal(base[:,0],latest[:,0])),"right":bool(np.array_equal(base[:,-1],latest[:,-1]))}
old=json.loads((Z/"qa/assembly_r04_c04_candidate-v1_4096/qa_index.json").read_text())
new=json.loads((out/"seams/qa_index.json").read_text())
review=[]
for i,(a,b) in enumerate(zip(old["seamAndJunctionCrops"],new["seamAndJunctionCrops"])):
 same=a["sha256"]==b["sha256"]
 # All v1 verticals were inspected before foliage repair; all changed verticals and all horizontals/junctions re-inspected on v4.
 reused=i in [0,1,3,4,6,7,9,10,11]
 assert not reused or same
 review.append({**b,"viewedAtNative100Percent":True,"visualResult":"usable_internal_geometry_continuous","viewBasis":"v1 native crop verified byte-identical to v4" if reused else "v4 native crop directly viewed","samePngBytesAsV1":same})
data={"schemaVersion":1,"tileId":"r04_c04","reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"status":"internal_native_visual_review_passed_external_edges_pending","selectedCandidate":{"path":str(tile),"sha256":sha(tile),"dimensions":[4096,4096],"record":{"path":str(record),"sha256":sha(record)}},"sourceLineage":"16 builtin native patches in explicit v1 assembly; three same-coordinate native foliage edits selected with recorded binary masks; no resized final pixels","sourceValidation":{"path":str(out/"provenance_validation.json"),"sha256":sha(out/"provenance_validation.json"),"method":"apply_native_tile_repair --validate-base-only","passed":True},"internalReview":{"33NativeCropsReviewed":True,"coverage":new["coverage"],"crops":review,"railAndPillars":"continuous straight railing and correctly connected two sphere-topped pillars in whole-tile composition; no further internal geometry repair identified","paving":"existing staggered/cut paving grid and joints continuous at native internal joins; microscopic surface variation retained","foliage":"initial optical blur corrected; initial edit top/bottom partial-leaf borders repaired by two additional overlapping native edits; all repair-boundary contexts and three combined native crop images reviewed"},"outermostEdgesByteIdenticalToV1":edge,"externalReview":{"accepted":False,"owner":"root connected tile review","remaining":["North external edge against r03_c04 final tile requires connected QA.","West edge against r04_c03 latest v5 roof repair requires connected QA.","Known bottom-left red lantern spans r04/r05 and c03/c04; preserve unresolved cross-corner issue for native joint repair after next lower tiles are ready."],"formalAccepted":False},"sharedProgressModified":False,"sharedSelectedManifestModified":False}
p=out/"visual_review.json"
with p.open("x",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps({"review":str(p),"sha256":sha(p),"all4OutermostEdgesUnchanged":all(edge.values()),"status":data["status"]}))

