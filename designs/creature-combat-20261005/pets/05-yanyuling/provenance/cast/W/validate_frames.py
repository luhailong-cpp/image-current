from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
B=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling")
D=B/"provenance/cast/W"
items=[]
for n in range(1,17):
 s=f"{n:02d}"; p=B/"runtime/cast/W"/f"{s}.png"; r=json.loads((D/f"{s}.generation.json").read_text(encoding="utf-8"))
 im=Image.open(p); a=im.getchannel("A"); h=hashlib.sha256(p.read_bytes()).hexdigest()
 checks={"size":im.size==(1024,1024),"mode":im.mode=="RGBA","transparency":a.getextrema()==(0,255),"sha256Matches":h==r["sha256"],"promptExists":Path(r["prompt"]).is_file(),"receiptExists":Path(r["evidence"]["receipt"]).is_file(),"referencesMatch":all(hashlib.sha256(Path(q["path"]).read_bytes()).hexdigest()==q["sha256"] for q in r["references"])}
 items.append({"frame":n,"file":str(p),"sha256":h,"alphaBBox":a.getbbox(),"checks":checks})
result={"createdAt":datetime.now(timezone.utc).isoformat(),"action":"cast","direction":"W","frameCount":len(items),"expectedCount":16,"uniqueSha256":len({x["sha256"] for x in items}),"passed":all(all(x["checks"].values()) for x in items) and len({x["sha256"] for x in items})==16,"durationMs":45,"totalDurationMs":720,"perFrameNativeVisualReview":"all 16 final native results viewed individually","playbackReview":"delegated to root final six-group playback; not claimed here","clientIntegration":"not performed","frames":items}
(D/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))

