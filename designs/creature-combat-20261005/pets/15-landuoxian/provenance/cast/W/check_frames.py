from pathlib import Path
from PIL import Image
import json,hashlib
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian")
prov=base/"provenance/cast/W"
rows=[]
for n in range(1,17):
 p=base/"runtime/cast/W"/f"{n:02d}.png"
 im=Image.open(p)
 rec=json.loads((prov/f"{n:02d}.generation.json").read_text(encoding="utf-8"))
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 rows.append({"frame":n,"file":str(p),"sha256":sha,"recordShaMatches":sha==rec["sha256"],"size":list(im.size),"mode":im.mode,"alphaExtrema":list(im.getchannel("A").getextrema()),"bbox":list(im.getchannel("A").getbbox()),"promptExists":Path(rec["prompt"]).exists(),"receiptExists":Path(rec["evidence"]["receipt"]).exists(),"nativeShaMatches":hashlib.sha256(Path(rec["native"]["file"]).read_bytes()).hexdigest()==rec["native"]["sha256"]})
rep={"frameCount":len(rows),"uniqueShaCount":len(set(r["sha256"] for r in rows)),"technicalPassed":all(r["recordShaMatches"] and r["size"]==[1024,1024] and r["mode"]=="RGBA" and r["alphaExtrema"]==[0,255] and r["promptExists"] and r["receiptExists"] and r["nativeShaMatches"] for r in rows),"dynamicStatus":"not-reviewed-live-playback","gameIntegration":"not-tested","rows":rows}
(prov/"technical-check.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in rep.items() if k!="rows"}))

