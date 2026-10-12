from pathlib import Path
import json,hashlib,subprocess,sys
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=D/"p03_03-coordination-v02/request.json";req=json.loads(q.read_text());req["originalSavedRequest"]={"file":str(q),"sha256":sha(q)}
req["guideDerivationMetadata"]={k:v for k,v in req["coordinates"].items() if k not in ["id","row","column","coreWorldBox","contextWorldBox","nativeCoreBox"]}
req["coordinates"]={k:req["coordinates"][k] for k in ["id","row","column","coreWorldBox","contextWorldBox","nativeCoreBox"]}
req["registrationNormalization"]="Only local coordinate metadata shape normalized; actual tool prompt and references are byte-for-byte unchanged."
reg=D/"p03_03-coordination-v02/request-registration.json";reg.write_text(json.dumps(req,indent=2),encoding="utf-8")
selected=[("p01_01","p01_01-geometry-quiet-v01"),("p01_03","p01_03-quiet-material-v02"),("p02_02","p02_02-geometry-quiet-v01"),("p03_03","p03_03-coordination-v02")]
decisions=[]
for patch,attempt in selected:
 folder=D/attempt;request=reg if patch=="p03_03" else folder/"request.json";receipt=folder/"receipt.json"
 rr=json.loads(receipt.read_text());di={"id":patch,"attempt":attempt,"sha256":rr["savedNativeSha256"],"selectedAs":"improved provisional native; whole tile and seam QA pending","formalAccepted":False}
 if patch=="p03_03":di.update(localGeometry="two Y arms present and unwanted extensions removed",material="line contrast differs from neighbor; seam tone pending",sharedEdge="D3/Y heads within4px at x115; lower rim differs17px from p0302; not boundary accepted")
 elif patch=="p01_03":di.update(localGeometry="complete X restored; material edit retains sampled line centers within1px",material="quiet enough for joined review; macro left entry differs55px from original coarse estimate and needs reconciliation")
 else:di.update(localGeometry="all required topology present and matches explicit approved-coordinate guide",material="broad low contrast quiet stone, local pass",sharedEdge="pending joined inspection")
 (folder/"qa-review.json").write_text(json.dumps(di,indent=2),encoding="utf-8")
 cmd=[sys.executable,str(B.parent/"pipeline-tools/register-native-version.py"),"r12_c05",patch,attempt,str(request),str(receipt)]
 r=subprocess.run(cmd,text=True,capture_output=True);assert r.returncode==0,r.stderr;di["registrationResult"]=json.loads(r.stdout);decisions.append(di)
(D/"selection-round-01.json").write_text(json.dumps(decisions,indent=2),encoding="utf-8")
print(json.dumps(decisions,indent=2))

