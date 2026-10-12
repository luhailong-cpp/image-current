from pathlib import Path
import json,hashlib,datetime
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14")
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
for p in (t/"native").glob("*.generation.json"):
 d=json.loads(p.read_text(encoding="utf-8")); src=Path(d["evidence"]["originalOutputPath"]); native=Path(d["file"])
 assert h(src)==h(native)==d["sha256"]
 assert h(d["evidence"]["receipt"])==d["evidence"]["receiptSha256"]
 records.append(d)
outs=list(Path(r"C:/Users/luyua/.codex/generated_images/01a1256f-f474-7161-a84b-6c353e51fc2f").glob("*.png"))
used={str(Path(d["evidence"]["originalOutputPath"]).resolve()).lower() for d in records}
pending=[str(p) for p in outs if str(p.resolve()).lower() not in used]
active=json.loads((t/"active-native-map.json").read_text(encoding="utf-8"))
assert len(active)==16 and len(records)==18 and not pending
m=json.loads((t/"candidate/latest-assembly.json").read_text(encoding="utf-8"))
assert h(m["candidate"]["path"])==m["candidate"]["sha256"]
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"generatedOutputCount":len(outs),"nativeGenerationRecordCount":len(records),"activeCoordinateCount":len(active),"pendingSuccessfulOutputs":pending,"alreadyIngestedSupersededCount":len(records)-len(active),"candidate":m["candidate"],"conclusion":"All18 successful originals already byte-identical ingested. Both prior repair outputs retained in active16 and initial candidate. No unmerged passing native output found; no repeated generation needed.","originalOutputs":[{"path":str(p),"sha256":h(p)} for p in outs]}
out=t/"review/recovery-audit-20261011.json"
if out.exists():assert json.loads(out.read_text())["pendingSuccessfulOutputs"]==[]
else:out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="originalOutputs"}))

