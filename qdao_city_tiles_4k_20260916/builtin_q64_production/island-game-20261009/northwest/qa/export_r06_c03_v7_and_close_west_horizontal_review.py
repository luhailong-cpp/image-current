from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");sys.path.insert(0,str(Z));import assemble_tile as a
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
q=Z/"qa/r04_c02_v9_internal_review/qa_index.json";data=json.loads(q.read_text())
items=[i for i in data["seamAndJunctionCrops"] if Path(i["path"]).name.startswith("top-bottom")]
assert len(items)==12
notes=["Wall base, pillar corner, plant/pavement boundary and pavement joints continuous.","Stone panel grooves, carved floral pillar faces and masonry transitions continuous.","Wall cap perspective, shadow texture and foliage boundary continuous.","Stone pillar faces and carvings complete, cap-to-wall join continuous.","Flower and branch layers and exposed paving edges continuous.","Large stone joints and roof curl silhouette continuous.","Wall base, paving grout and exposed roof corner continuous.","Curved gold/red roof ridge and blue tile contacts complete.","Tree branches and dense blossoms continuous without cut layers.","Blue tile ends, gold floral caps and timber/roof contact lines align.","Full repeated blue tile courses align with continuous arc rims.","Gold central ridge, red side edges and blue tiles align."]
out=[]
for i,n in zip(items,notes):
 assert sha(Path(i["path"]))==i["sha256"]
 out.append({**i,"status":"pass","notes":n,"method":"Independently viewed complete crop using view_image detail=original"})
p=Z/"qa/r04_c02_v9_independent_connected_12_review_20261012.json";assert not p.exists()
p.write_text(json.dumps({"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"reviewer":"connected_closure","qaIndex":info(q),"status":"pass_12_horizontal_native_seam_crops","count":12,"items":out,"scope":"Only these twelve horizontal seam crops; no whole tile acceptance assertion."},indent=2)+"\n",encoding="utf8")
print(info(p))
v=Z/"tiles/r06_c03_candidate-v7_4096.png";assert sha(v)=="8d729be772ccbd51f9599b04d70a7505e4d71c052fb0aedf8ce4f4e65af5bee1"
d=Z/"qa/r06_c03_v7_internal_closure_20261012";assert not d.exists();d.mkdir()
qa=a.save_qa(d,Image.open(v).convert("RGB"));qa["base"]=info(v);qa["record"]=info(v.with_suffix(".native-repair.json"))
(d/"qa_index.json").write_text(json.dumps(qa,indent=2)+"\n",encoding="utf8")
prior=json.loads((Z/"qa/assembly_r06_c03_candidate-v1_4096/qa_index.json").read_text())
old={Path(c["path"]).name:c for c in prior["seamAndJunctionCrops"]}
changed=[c for c in qa["seamAndJunctionCrops"] if c["sha256"]!=old[Path(c["path"]).name]["sha256"]]
same=[c for c in qa["seamAndJunctionCrops"] if c["sha256"]==old[Path(c["path"]).name]["sha256"]]
for name,box in [("paving_left_lower_join_100pct.png",[1750,900,3004,2154]),("paving_lower_full_100pct.png",[2842,1000,4096,2254]),("sphere_and_three_courses_100pct.png",[2842,600,4096,1854]),("roof_final_join_100pct.png",[1500,2842,2754,4096])]:
 p=d/name;Image.open(v).crop(box).save(p);qa.setdefault("extraCrops",[]).append({**info(p),"tileCropBox":box,"nativeScale100Percent":True})
(d/"qa_index.json").write_text(json.dumps(qa,indent=2)+"\n",encoding="utf8")
(d/"review_pending.json").write_text(json.dumps({"status":"pending","changedStandardCrops":changed,"unchangedStandardCrops":same,"unchangedMayReuseOnlyExactHashPreviousPassedVerdict":True,"extras":qa["extraCrops"]},indent=2)+"\n",encoding="utf8")
print(json.dumps({"qaIndex":info(d/"qa_index.json"),"changed":[Path(c["path"]).name for c in changed],"unchanged":len(same)}))

