from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");D=Z/"qa/r06_c03_v7_internal_closure_20261012"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
q=json.loads((D/"qa_index.json").read_text());p=json.loads((D/"review_pending.json").read_text())
prev=Z/"qa/r06_c03_v1_independent_connected_review_20261012.json"
old={Path(x["path"]).name:x for x in json.loads(prev.read_text())["standardCrops"]}
changed={Path(c["path"]).name for c in p["changedStandardCrops"]}
changedNotes=[
"Stone edges and moss junctions continuous; new internal mottling joins previous material without a hard source outline.",
"Both prior thick grout blind ends are resolved into continuous plausible slab boundaries.",
"Repaired lower slab surface has no former horizontal texture cut; foliage and slab geometry continuous.",
"Slab outlines and shadow are continuous alongside the pillar; new lower texture selected only within paving.",
"Roof fascia edge has no blue notch; curl, gold cap and neighboring tiles continuous.",
"Previously displaced blue tile rims are now connected through complete strip to the south boundary.",
"All large stone boundaries and tree edge continuous across the horizontal band.",
"New slab surface and coarse joints align with the flowers/leaf boundary.",
"Sphere detail is now crisp and geometry continuous; east-adjacent top-rail softness remains explicitly in the whole-object cross-tile repair scope.",
"Foliage boundary and exposed paving coarse seams remain continuous; old east strip material pending cross-tile work.",
"Blue roof course junctions and roof fascia are continuous.",
"Gold/red roof edge and foliage align with blue tiles at left.",
"Stone four-source junction and lower surface texture remain continuous.",
"Pillar silhouette and stone four-source junction align.",
"Red fascia and adjacent blue tiles now align at the four-source junction."
]
notes=dict(zip([Path(c["path"]).name for c in p["changedStandardCrops"]],changedNotes))
items=[]
for c in q["seamAndJunctionCrops"]:
 n=Path(c["path"]).name;assert sha(Path(c["path"]))==c["sha256"]
 if n in changed:
  method="Viewed complete final native crop using view_image detail=original";note=notes[n]
 else:
  assert c["sha256"]==old[n]["sha256"] and old[n]["geometryStatus"]=="pass"
  method="Exact SHA256 identity with already independently viewed native crop; prior geometry verdict reused";note=old[n]["notes"]
 items.append({**c,"seamGeometryStatus":"pass","reviewMethod":method,"notes":note,"wholeMaterialAcceptance":False if ("r01" in n or n=="left-right_r02_c03-c04_100pct.png") else None})
extras=[]
for e in q["extraCrops"]:
 assert sha(Path(e["path"]))==e["sha256"]
 n=Path(e["path"]).name
 note={"paving_left_lower_join_100pct.png":"Former horizontal texture cut eliminated; slab outline, vegetation and selection surroundings continuous.","paving_lower_full_100pct.png":"Three selected pavement exposures continuous; carved pillar, courses and large flower/leaf field preserved. Eastern old texture explicitly pending.","sphere_and_three_courses_100pct.png":"Sphere and carved shaft crisp; three course contours continuous within tile. Upper rail remains softened towards tile x~3700..4096, not merely the rightmost115; repair together with the full cross-tile railing object.","roof_final_join_100pct.png":"Complete red/gold fascia and repeated blue tile courses continuous to south boundary; no repaired seam recurrence."}[n]
 extras.append({**e,"geometryStatus":"pass","materialStatus":"cross_tile_rail_clarity_pending" if n=="sphere_and_three_courses_100pct.png" else "local_scope_pass","method":"Viewed entire final1254 native crop using view_image detail=original","notes":note})
base=Path(q["base"]["path"]);v3=Z/"tiles/r06_c03_candidate-v3_4096.png"
a=np.asarray(Image.open(base).convert("RGB"));b=np.asarray(Image.open(v3).convert("RGB"))
bands={"north115":(slice(0,115),slice(None)),"south115":(slice(-115,None),slice(None)),"west115":(slice(None),slice(0,115)),"east115":(slice(None),slice(-115,None))}
preserve={k:bool(np.array_equal(a[ss],b[ss])) for k,ss in bands.items()};assert all(preserve.values())
assert np.array_equal(a[2254:],b[2254:])
for folder,note in [("r06_c03_paving_natural_lower_mask_v2","Restricted to three exposed pavement regions; pillar, three courses and large foliage field unchanged. Local continuity passed."),("r06_c03_paving_lower_join_mask_v1","Former horizontal internal stone texture edge removed; coarse joints and leaf edges continuous.")]:
 d=Z/"qa"/folder;rp=d/"visual_review.json";assert not rp.exists()
 save(rp,{"status":"pass_local_selected_repair","combined":info(d/"combined_native_crop.png"),"mask":info(d/"source_selection_mask.png"),"reviewers":[{"agent":"connected_closure","method":"complete original1254 visual view","result":"pass"},{"agent":"root","method":"independent complete original1254 view, reported by collaboration message","result":"pass"}],"notes":note,"wholeTileAcceptance":False})
rec={"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"internal_native_seam_geometry_pass_shared_object_pending","tileId":"r06_c03","base":q["base"],"record":q["record"],"qaIndex":info(D/"qa_index.json"),"priorReview":info(prev),"strictNativeReplay":info(D/"strict_native_replay.json"),"nativePixelCountVerified":16777216,"nativeSeamGeometryPassed":33,"newFinalStandardCropsViewed":15,"hashIdenticalPriorPassedCrops":18,"extraNativeCropsViewed":4,"standardCrops":items,"extraCrops":extras,"preservationAgainstV3":{"base":info(v3),"outer115":preserve,"allRowsFrom2254To4096ExactlyUnchanged":True,"r07SouthAnchorStillExactV3":True},"materialScope":{"largeRectangularPatchPattern":"substantially replaced by irregular mineral mottling and cracks in selected interior pavement","fineGrain":"fine square-like grain remains near original anchor; root accepts this local naturalization basis, west independently flagged residual regularity; do not claim all microscopic grid removed","oldNorthEast115":"preserved exactly for connected boundary handling"},"pendingCrossTile":["East-adjacent rail softness extends approximately tile x3700..4096; reconstruct/clarify with complete shared c03/c04 railing object and its column anchors.","East115 paving still old regular pattern; coordinate natural material across neighbor.","Next r05/r06 shared horizontal and vertical seams and four-tile intersection require connected QA."],"formalAcceptedCount":0,"globalProgressModified":False}
rp=D/"visual_review.json";assert not rp.exists();save(rp,rec)
cp=D/"closure.json";assert not cp.exists();save(cp,{k:rec[k] for k in ["createdAtUtc","status","tileId","base","record","qaIndex","strictNativeReplay","nativePixelCountVerified","nativeSeamGeometryPassed","newFinalStandardCropsViewed","hashIdenticalPriorPassedCrops","extraNativeCropsViewed","preservationAgainstV3","materialScope","pendingCrossTile","formalAcceptedCount"]}|{"visualReview":info(rp)})
print(json.dumps({"review":info(rp),"closure":info(cp),"strict":info(D/"strict_native_replay.json"),"outer115":preserve}))

