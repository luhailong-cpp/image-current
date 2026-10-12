from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
tile="r12_c05";patch="p02_01";D=B/tile
receipt=D/"pipeline/receipts/p02_01.geometry-v02.receipt.json"
rec=json.loads(receipt.read_text());src=Path(rec["sourceOutputPath"])
request=D/"refinement/p02_01.geometry-v02.request.json";req=json.loads(request.read_text())
target=D/"refinement/native/p02_01.png";target.parent.mkdir(exist_ok=True)
assert not target.exists()
im=Image.open(src);assert im.size==(1254,1254) and im.format=="PNG"
shutil.copy2(src,target)
original=json.loads((D/"native/p02_01.png.generation.json").read_text())
original.update(file=str(target),sha256=sha(target),sourceOutputPath=str(src),sourceOutputSha256=sha(src),generatedAt=datetime.now(timezone.utc).isoformat(),prompt=req["promptFile"],promptSha256=req["promptSha256"],request=str(request),requestSha256=sha(request),references=req["references"],visualStatus="geometry_improved_material_pending",refinementOf=str(D/"native/p02_01.png"))
original["evidence"]={"toolReceipt":str(receipt),"toolReceiptSha256":sha(receipt),"pngMetadata":{}}
record=Path(str(target)+".generation.json");atomic_json(record,original)
selection=D/"refinement/selection.json";sel=json.loads(selection.read_text()) if selection.exists() else {};sel[patch]="refinement/native/p02_01.png.generation.json";atomic_json(selection,sel)
handoff=B/"continuation-round-20261011.json";d=json.loads(handoff.read_text())
d["resumedAt"]="2026-10-11T08:50:14.568Z";d["resumedAtEvidence"]="Timestamp of first actual builtin call of this full64 continuation, from firstNewOutputThisContinuation receipt."
d["recordedAtUtc"]=datetime.now(timezone.utc).isoformat()
d["firstNewOutputAfterLatestAuthorization"]={"startedAtUtc":rec["startedAtUtc"],"recordedAtUtc":rec["recordedAtUtc"],"file":str(src),"sha256":sha(src),"receipt":str(receipt),"tile":tile,"patch":patch,"kind":"refinement; no new spatial coverage"}
d["network"].update(rootNewCallRejected=False,lastRootCallStartedAt=rec["startedAtUtc"],lastRootCallReturnedImage=True,latestAuthorizationUtc="2026-10-11T09:51:50Z",currentBuiltinSuccessVerified=True,workerErrorAfterLatestAuthorizationVerified=False,timingAuditConclusion="Worker reported zero network calls and no actual fatal receipt. Saved object-plane proposal predates latest authorization; root successfully continued afterward.")
d["nextSteps"]=["Integrate saved G01 object contact and stair color improvements.","Continue native coverage in assigned exclusive columns.","Correct dense stone material across existing affected candidates before formal QA."]
atomic_json(handoff,d)
print(json.dumps({"native":str(target),"sha256":sha(target),"selection":str(selection),"handoff":str(handoff)},indent=2))
