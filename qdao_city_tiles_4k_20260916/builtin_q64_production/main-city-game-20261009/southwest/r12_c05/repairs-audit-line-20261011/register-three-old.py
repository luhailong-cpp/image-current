from pathlib import Path
import subprocess,sys,json
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";out=[]
for patch in ["p01_03","p02_03","p02_04"]:
 attempt=patch+"-coherent-geometry-v03";f=D/attempt;r=json.loads((f/"receipt.json").read_text())
 qa={"id":patch,"attempt":attempt,"sha256":r["savedNativeSha256"],"localGeometry":"approved diagram topology present; X/T endpoints and color boundary positions substantially corrected","material":"quiet neutral limestone locally acceptable","sharedEdges":"reassembly pending; raw visual position deviations remain possible","formalAccepted":False,"internalAccepted":False}
 (f/"qa-review.json").write_text(json.dumps(qa,indent=2))
 p=subprocess.run([sys.executable,str(B.parent/"pipeline-tools/register-native-version.py"),"r12_c05",patch,attempt,str(f/"request.json"),str(f/"receipt.json")],capture_output=True,text=True);assert p.returncode==0,p.stderr
 out.append(qa)
(D/"selection-three-old-round-03.json").write_text(json.dumps(out,indent=2));print(json.dumps(out))

