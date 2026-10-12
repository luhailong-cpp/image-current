from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;b=w.parent
ident=sys.argv[1];row=int(ident.split("_")[2][1:]);col=int(ident.split("_")[3][1:]);f=b/"native"/(ident+".png")
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
write=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
r={"file":str(f),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"row":row,"column":col,"status":"selected-pending-full-tile-QA"}
write(w/"selections"/f"s{row:02d}_s{col:02d}.json",r)
qa={"reviewedAt":datetime.now(timezone.utc).isoformat(),"native":r,"dimensions":[1254,1254],"neighborPairAccepted":True,"inspectedAt100Percent":sys.argv[2:],"findings":"Native rope, knot and open mesh continuity reviewed at actual pixel scale; no duplicated support or clipped strand. Exact source composition required for final tile.","formalAccepted":False}
write(w/"qa"/(ident+".visual-qa.json"),qa)
p=read(w/"progress.json");p.update(generationOutputs=len(list((b/"native").glob("r05_c03*.png"))),selectedCandidateFragments=len(list((w/"selections").glob("*.json"))),inFlight=False,status="native-production-resumed",lastSelected=ident,next="Continue connected native fragments from selected neighbors");write(w/"progress.json",p)
print(json.dumps({"selected":ident,"count":p["selectedCandidateFragments"]}))

