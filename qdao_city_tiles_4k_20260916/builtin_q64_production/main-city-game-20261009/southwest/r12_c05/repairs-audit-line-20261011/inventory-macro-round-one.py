from pathlib import Path
from PIL import Image
import json,hashlib,datetime
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sel=json.loads((B/"refinement/selection.json").read_text());selected={}
for k,v in sel.items():
 rec=json.loads((B/v).read_text());selected[rec["sha256"]]=k
rejected={"p01_02-macro-rebuild-v02":"Correct right heads but northwest/top joint entries shifted beyond source uncertainty; replaced by explicit geometry.","p02_02-macro-rebuild-v01":"Missing left arm of X, lower T shifted.","p02_02-macro-rebuild-v02":"X arm restored but corner and lower T drifted; superseded by explicit diagram rendering."}
items=[]
for receipt in sorted(D.glob("*/receipt.json")):
 rr=json.loads(receipt.read_text());native=receipt.parent/"native.png";req=receipt.parent/"request.json"
 digest=sha(native);assert digest==rr.get("savedNativeSha256",rr.get("nativeSha256",digest))
 im=Image.open(native);assert im.size==(1254,1254)
 item={"attempt":receipt.parent.name,"native":str(native),"sha256":digest,"receipt":str(receipt),"receiptSha256":sha(receipt),"request":str(req),"requestSha256":sha(req),"dimensions":list(im.size),"actualModel":None,"actualQuality":None,"resizedAfterGeneration":False,"formalAccepted":False}
 if digest in selected:item.update(disposition="selected provisional improvement",selectedSlot=selected[digest])
 elif receipt.parent.name in rejected:item.update(disposition="rejected",reason=rejected[receipt.parent.name])
 elif receipt.parent.name in {"p01_01-explicit-geometry-v01","p01_02-explicit-geometry-v01","p01_03-macro-rebuild-v01","p01_04-explicit-geometry-v01","p02_01-explicit-geometry-v01","p02_02-explicit-geometry-v03","p03_03-coordination-v01"}:item.update(disposition="source reused by later genuine builtin refinement; superseded",reason="Kept immutable with request/receipt; improved successor selected, not a missing unassembled slot.")
 else:item.update(disposition="new saved output awaiting visual QA and selection",reason="No disposition inferred from file existence.")
 items.append(item)
report={"schemaVersion":1,"tile":"r12_c05","createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"successCount":len(items),"selectedNewSlotCount":sum(x["disposition"].startswith("selected") for x in items),"failedNoImageAttempts":[{"file":str(D/"p01_02-macro-rebuild-v02/failure-receipt-01.json"),"reason":"generic connection failed; subsequent retry succeeded"}],"formalAccepted":False,"candidateAssembly":"pipeline/output/3bd6fffd207bcdf3/assembly.json","items":items,"remaining":["native joined edge geometry and material transitions","third/fourth-row frame topology and exact coherent blue boundaries","roof shared crop continuity","external tile neighbors pending"],"oldNativeAndFixedRefinementPreserved":True}
(D/"inventory-after-macro-round-01.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({"successCount":len(items),"selectedNewSlotCount":report["selectedNewSlotCount"],"report":str(D/"inventory-after-macro-round-01.json")}))

