from pathlib import Path
import json,hashlib,sys,shutil
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent;SW=B.parent
sys.path.insert(0,str(SW));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
patch=sys.argv[1];receipt=D/(patch+"-quiet-material-v01.receipt.json");request=D/(patch+"-quiet-material-v01.request.json")
rr=json.loads(receipt.read_text());req=json.loads(request.read_text());src=Path(rr["sourceOutputPath"])
target=B/"refinement/native"/(patch+".png");target.parent.mkdir(exist_ok=True);assert not target.exists()
im=__import__("PIL.Image",fromlist=["Image"]).open(src);assert im.size==(1254,1254)
shutil.copy2(src,target)
rec=json.loads((B/"native"/(patch+".png.generation.json")).read_text())
rec.update(file=str(target),sha256=sha(target),sourceOutputPath=str(src),sourceOutputSha256=sha(src),generatedAt=datetime.now(timezone.utc).isoformat(),prompt=req["promptFile"],promptSha256=req["promptSha256"],request=str(request),requestSha256=sha(request),references=req["references"],visualStatus="local_material_pass_boundary_QA_pending",refinementOf=str(B/"native"/(patch+".png")))
rec["evidence"]={"toolReceipt":str(receipt),"toolReceiptSha256":sha(receipt),"pngMetadata":{}}
atomic_json(Path(str(target)+".generation.json"),rec)
selection=B/"refinement/selection.json";sel=json.loads(selection.read_text()) if selection.exists() else {};sel[patch]="refinement/native/"+patch+".png.generation.json";atomic_json(selection,sel)
print(json.dumps({"native":str(target),"sha256":sha(target),"selected":patch}))
