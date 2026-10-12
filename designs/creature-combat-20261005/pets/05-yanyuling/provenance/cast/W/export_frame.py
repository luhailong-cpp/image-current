from pathlib import Path
from PIL import Image
import json, hashlib, sys
from datetime import datetime, timezone
BASE=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling")
D=BASE/"provenance/cast/W"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
n=int(sys.argv[1]); s=f"{n:02d}"
receipt=json.loads((D/f"{s}.receipt.json").read_text(encoding="utf-8"))
src=Path(receipt["sourcePath"])
out=BASE/"runtime/cast/W"/f"{s}.png"
out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src)
native={"path":str(src),"sha256":sha(src),"width":im.width,"height":im.height,"format":im.format,"mode":im.mode}
im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
refs=[]
roles=["existing E identity, palette and anatomy", "existing W identity, true rear camera and accessory sides", "primary approved hand-painted style and materials"]
for i,p in enumerate(receipt["submittedParameters"]["referenced_image_paths"]):
 refs.append({"path":p,"sha256":sha(p),"role":roles[i] if i<3 else "previous accepted W frame, camera and scale continuity"})
config=json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
record={"file":str(out),"sha256":sha(out),"action":"cast","direction":"W","frame":n,"durationMs":45,"pivot":[0.5,0.08],"generatedAt":receipt["observedCompletionAt"],"tool":"image_gen.imagegen","route":"builtin","configSnapshot":config,"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":receipt["submittedParameters"]["referenced_image_paths"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host managed; tool schema does not expose model/quality selectors and result does not disclose actual model or quality.","evidence":{"receipt":str(D/f"{s}.receipt.json"),"fields":["returnedKeys","output_hint"]},"prompt":str(D/f"{s}.prompt.txt"),"references":refs,"nativeOutput":native,"width":1024,"height":1024,"format":"PNG","mode":"RGBA","derivedFrom":{"path":str(src),"sha256":native["sha256"]},"operation":{"type":"whole_canvas_uniform_resize","sourceSize":[im.width,im.height],"outputSize":[1024,1024],"resampler":"LANCZOS","perFrameAlignment":False},"visualReview":{"status":"inspected","notes":sys.argv[2]}}
(D/f"{s}.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":n,"file":str(out),"nativeSize":[im.width,im.height],"sha256":record["sha256"],"alphaExtrema":Image.open(out).getchannel("A").getextrema()},ensure_ascii=False))

