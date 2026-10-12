from pathlib import Path
import json, hashlib, datetime

Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
q=Z/"qa/assembly_r06_c03_candidate-v1_4096/qa_index.json"
base=Z/"tiles/r06_c03_candidate-v1_4096.png"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(q)=="dc5b9953470b2902d65dd4ee799d2d68172c68ebf11a0988a41d0b9051ab42c1"
assert sha(base)=="882578abcfe382bb3fc91431a66a57110eec32172c75beabdaeafab6b5bb4d78"
idx=json.loads(q.read_text(encoding="utf-8"))
notes=[
"Large stone joints and highlights remain continuous; small red paper pieces are intact.",
"Large stone edges continue across the vertical join. Increasing square surface pattern is a separate material concern.",
"Two thick diagonal stone joints terminate abruptly near local (210,175) and (240,355), tile approximately (3042,175) and (3072,355).",
"Paving outline, blossom petals, buds and branches continue without a visible cut.",
"Paving-to-foliage edge and crossing branches are coherent; no visible severed object.",
"Paving seams, pillar edge, leaves and shadow continue geometrically; square paving pattern is a separate concern.",
"Blossom/branch layers and red-gold roof edge align; no abrupt source boundary.",
"Red roof fascia intrudes into blue tiles near tile (2000,3040); linked to lower blue-tile alignment defect.",
"Tree trunk and leaf clusters remain continuous through full strip.",
"Blue cylindrical tiles align through the strip with continuous arc rims and highlight strokes.",
"Repeated blue-tile rims and dark joints are cut at local x approximately 170..230, y 350..1139, tile approximately x 1978..2038, y 3307..4096; reaches the south perimeter.",
"Branches, foliage and red-gold roof edge remain continuous.",
"Large slab grid and blossoms are continuous across the horizontal join.",
"Large stone joints and leaf boundary are continuous.",
"Large stone joints are continuous; square internal stone pattern remains a separate material issue.",
"Pillar and horizontal courses are geometrically connected, but ball finial and upper rail are visibly defocused compared with the carved shaft.",
"Petals, branches and leaf shadows flow continuously.",
"Flower clusters and branches align without a cut or repeated fragment.",
"Branches and leaf silhouettes are continuous.",
"Leaves, shadows and exposed paving joints are continuous.",
"Red-gold roof ridge and blue tile caps connect consistently.",
"Right edge shows the roof fascia notch and adjacent blue tile source displacement, the same defect as the vertical strip.",
"Red-gold roof edge, blue tiles visible at left, and foliage have continuous local geometry.",
"Branches and leaf groups are continuous, including the larger fork at upper right.",
"Stone crossing, red paper and blossoms are coherent at four-source junction.",
"Stone crossing and foliage edge are continuous at the junction.",
"Stone joints and pillar silhouette align. Paving material concern remains separate.",
"Blossoms, foliage and branch layering are continuous.",
"Leaf and blossom layers and the roof curl edge remain coherent.",
"Leaves and diagonal trunk remain continuous.",
"Blue tile arc rims and fascia are aligned at the four-source junction.",
"Four-source junction contains a displaced blue tile dark joint and red fascia intrusion, matching the roof repair area.",
"Leaf clusters and trunk shading are continuous."
]
bad={2:["paving_blind_ends"],7:["roof_fascia_and_blue_tile_join"],10:["roof_fascia_and_blue_tile_join"],21:["roof_fascia_and_blue_tile_join"],31:["roof_fascia_and_blue_tile_join"]}
texture={0,1,2,3,4,5,12,13,14,15,19,24,25,26}
items=[]
for i,c in enumerate(idx["seamAndJunctionCrops"]):
    assert sha(c["path"])==c["sha256"]
    items.append({**c,"geometryStatus":"needs_repair" if i in bad else "pass","findingIds":bad.get(i,[]),"materialStatus":"needs_local_clarity_repair_and_paving_review" if i==15 else ("paving_pattern_concern_separate_from_geometry" if i in texture else "pass"),"reviewMethod":"Direct view_image detail=original; image displayed individually or in a small batch at native resolution; no preview or numeric proxy used for visual verdict.","notes":notes[i]})
ei=Z/"qa/r06_c03_v1_extra_20261012/index.json"
e=json.loads(ei.read_text(encoding="utf-8"))
extra=[]
for name,note,status in [
("paving_material_transition.png","Right half develops an orthogonal micro-grid and rectangular macro patches, compared with the irregular small stone texture at left. This is a real artificial paving-material transition from approximately tile x=2000 towards the right, and cannot be recorded as natural stone material PASS.","needs_material_resolution"),
("whole_stone_pillar_and_courses.png","Ball finial and top rail visibly defocused; geometry, shaft carving and horizontal rail connections are coherent. Agree with root local material-clarity repair.","needs_local_clarity_repair")
]:
    c=next(c for c in e["crops"] if Path(c["path"]).name==name)
    assert sha(c["path"])==c["sha256"]
    extra.append({**c,"status":status,"notes":note,"reviewMethod":"Direct view_image detail=original of complete 1254 native crop."})
out={"schemaVersion":1,"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"reviewer":"connected_closure independent visual review","status":"needs_repairs_not_tile_acceptance","base":{"path":str(base),"sha256":sha(base)},"qaIndex":{"path":str(q),"sha256":sha(q)},"summary":{"nativeStandardCropsViewed":33,"geometryPass":28,"geometryNeedsRepair":5,"uniqueGeometricRepairAreas":2,"additionalWholeObjectCropsViewed":2,"wholeTileAccepted":False},"findings":[{"id":"paving_blind_ends","tileApproximatePoints":[[3042,175],[3072,355]],"action":"Repair both thick stone-joint blind ends together."},{"id":"roof_fascia_and_blue_tile_join","tileApproximateBounds":[1970,3010,2070,4096],"action":"Repair red fascia notch together with the repeated blue-tile displacements down to the south edge. Subsequent r07 anchoring must use the resulting new south boundary."},{"id":"stone_pillar_clarity","action":"Localized clarity restoration to ball finial and upper rail; maintain geometry."},{"id":"paving_material_transition","action":"Resolve artificial square-grid surface pattern before claiming natural paving material acceptance; root owns final scope."}],"standardCrops":items,"extraCrops":extra,"preservation":{"qaIndexUnmodified":True,"imagePixelsUnmodified":True,"globalProgressUnmodified":True,"historicalFreezeUnmodified":True},"next":"Root owns native repair and assembly. Re-review changed native crops and preserve hash-identical prior geometry verdicts. r05/r06 connected assembly must wait for internal closure."}
p=Z/"qa/r06_c03_v1_independent_connected_review_20261012.json"
assert not p.exists()
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"path":str(p),"sha256":sha(p),"summary":out["summary"]}))

