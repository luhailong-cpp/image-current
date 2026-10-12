from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest")
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))
release=B.parent.parent/"resume-production-20261010/production-resume.json"
assignment=B.parent.parent/"acceleration-20261010/assignments.json"
ack={"schemaVersion":1,"acknowledgedAt":datetime.now(timezone.utc).isoformat(),"zone":"northwest","release":{"file":str(release),"sha256":hashlib.sha256(release.read_bytes()).hexdigest()},"newArtworkGenerationAllowed":load(release)["newArtworkGenerationAllowed"],"priorUserSuppliedAGENTSInstructionsApply":False,"runtimeWorkRequested":False,"builtinOnly":True,"paidApiAllowed":False,"preserveApprovedLayoutAndCoordinates":True,"currentTask":"Finish current 2x2 native composition and then remaining owned queue","assignmentReview":{"file":str(assignment),"sha256":hashlib.sha256(assignment.read_bytes()).hexdigest(),"ownedZoneExclusions":[]},"status":"art-production-resumed"}
(B/"resume-ack-20261010.json").write_text(json.dumps(ack,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for n in ["work-r03_c03/joint-final/joint-assembly.json","work-r04_c04/joint-west/final-v3/joint-assembly.json","work-r03_c04/joint-south-resume/proposal-v1/joint-assembly.json","work-r03_c04/paving-fresh/r03_c04.paving-proposal-v1.assembly.json"]:
 d=load(B/n)
 print(n, "\nKEYS", list(d.keys()), "\nSOURCE0", d["sources"][0], "\nARTIFACTS",d.get("artifacts"), "\nCANDIDATE",d.get("candidate"),"\nSOURCEID",d.get("sourceIdMap"))

