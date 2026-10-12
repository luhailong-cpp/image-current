from pathlib import Path
import json,hashlib,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
items=[("qa/r05_c03_door_wing_mask_v1/combined_native_crop.png","Door gold wing is complete and its outline/wood contact/selection boundary continuous.","pass"),("qa/r05_c03_stair_left_mask_v2/combined_native_crop.png","Treads, risers, left cheek and moss grout are continuous inside crop; rightmost boundary must be joined in next repair.","local_pass_right_boundary_dependent")]
checks=[]
for path,finding,status in items:
 p=Z/path;checks.append(dict(image=dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),native1254Viewed=True,finding=finding,status=status))
out=dict(schemaVersion=1,reviewer="/root/connected_closure",reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,wholeTileAccepted=False)
p=Z/"qa/r05_c03_independent_door_left_stair_review.json"
with p.open("x",encoding="utf8") as f:json.dump(out,f,indent=2)
p=Z/"qa/r05_c03_window_sill_repair_a01_mask_v1/root_independent_review.json"
with p.open("x",encoding="utf8") as f:json.dump(dict(reviewer="/root",evidence="Direct collaboration message: root viewed combined at native scale and passed",nativeVisualPassed=True,wholeTileAppliedByThisAgent=False),f,indent=2)

