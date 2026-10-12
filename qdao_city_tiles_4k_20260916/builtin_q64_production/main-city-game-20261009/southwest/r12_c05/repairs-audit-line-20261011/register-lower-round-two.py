from pathlib import Path
import json,subprocess,sys
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"
selected=[("p03_01","p03_01-neutral-stone-v02"),("p03_02","p03_02-neutral-stone-v02"),("p03_03","p03_03-coherent-geometry-v02"),("p04_01","p04_01-coherent-geometry-v02"),("p04_02","p04_02-coherent-geometry-v02")]
decisions=[]
for patch,attempt in selected:
 f=D/attempt;rr=json.loads((f/"receipt.json").read_text())
 di={"id":patch,"attempt":attempt,"sha256":rr["savedNativeSha256"],"selectedAs":"improved provisional native; full assembly seam QA pending","localGeometry":"required global-coordinate topology visibly present","material":"quiet broad stone; neutral gray and cream preserved; faint natural texture remains","formalAccepted":False,"internalAccepted":False,"sharedEdge":"pending actual reassembly"}
 (f/"qa-review.json").write_text(json.dumps(di,indent=2),encoding="utf-8")
 cmd=[sys.executable,str(B.parent/"pipeline-tools/register-native-version.py"),"r12_c05",patch,attempt,str(f/"request.json"),str(f/"receipt.json")]
 r=subprocess.run(cmd,text=True,capture_output=True);assert r.returncode==0,r.stderr
 di["registrationResult"]=json.loads(r.stdout);decisions.append(di)
(D/"selection-lower-round-02.json").write_text(json.dumps(decisions,indent=2),encoding="utf-8")
print(json.dumps([{"patch":x["id"],"sha256":x["sha256"]} for x in decisions]))

