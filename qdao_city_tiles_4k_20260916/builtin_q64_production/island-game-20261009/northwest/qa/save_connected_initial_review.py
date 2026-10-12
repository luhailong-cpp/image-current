from pathlib import Path
import json,hashlib,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest"); P=Z/"tiles/connected-r03-r04-c03-c04-v1"
c=json.loads((P/"connected-cluster.json").read_text(encoding="utf8"))
bad={"shared_vertical_y3072-4096_100pct.png":((4173,3088),"upper-edge paving grout disconnected"),
"shared_vertical_y4096-5120_100pct.png":((4260,4680),"parallel truncated paving grout"),
"shared_vertical_y5120-6144_100pct.png":((4240,5975),"short missing grout segment"),
"shared_horizontal_x1024-2048_100pct.png":((1245,4025),"diagonal grout fades and restarts")}
checks=[]
for q in c["qa"]["nativeScaleCrops"]:
 n=Path(q["output"]["path"]).name
 checks.append(dict(**q,actualNativeImageViewed=True,visualPassed=n not in bad,finding=bad[n][1] if n in bad else "Continuous object geometry/material at native scale",repairCenterCluster=bad[n][0] if n in bad else None))
out={"schemaVersion":1,"reviewedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"17 native cross-tile crops of explicit connected v1", "checks":checks,"passed":13,"repairRequired":4,"allSharedBoundariesPassed":False,"formalAcceptedCount":0,"remainingExterior":"All perimeter neighbors still require respective group check; south-edge large lantern spans future r04/r05 group."}
with (Z/"qa/connected-closure-v1.visual-review.json").open("x",encoding="utf8") as f:json.dump(out,f,ensure_ascii=False,indent=2)

