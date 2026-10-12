"""Apply reviewed local corrections without altering retained sprite pixels."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import json,hashlib,shutil,argparse
ROOT=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def inside(rel):
 p=(ROOT/rel).resolve();assert p.is_relative_to(ROOT);return p
ap=argparse.ArgumentParser();ap.add_argument("plan");args=ap.parse_args()
plan=rd(Path(args.plan));sel=rd(ROOT/"selection.json")
archive=ROOT/"provenance/grounding4-prior-records";archive.mkdir(exist_ok=True)
initial=ROOT/"provenance/grounding4-prior-selection.json"
if not initial.exists():wr(initial,sel)
# Preserve immutable text for edited inputs; no backup image is created.
for p in (ROOT/"runtime").rglob("*.png.generation.json"):
 dest=archive/str(p.relative_to(ROOT/"runtime")).replace("\\","--").replace("/","--")
 if not dest.exists():shutil.copyfile(p,dest)
index={(x["action"],x["direction"],int(x["frame"])):x for x in sel["frames"]}
keys=set();applied=[]
for fix in plan["replacements"]:
 d=fix["direction"];n=int(fix["frame"]);k=("run",d,n)
 assert d in ["N","NE","E","SE","S","SW","W","NW"] and 1<=n<=16 and k not in keys
 keys.add(k);row=index[k];target=inside(row["source"])
 native=inside(fix["nativeFile"]);nrpath=inside(fix.get("generationRecord",fix["nativeFile"]+".generation.json"))
 exported=inside(fix["exportFile"]);erpath=Path(str(exported)+".generation.json")
 nr=rd(nrpath);er=rd(erpath)
 assert sha(native)==nr["sha256"] and sha(exported)==er["sha256"]
 with Image.open(native) as im:assert min(im.size)>=1024 and im.mode=="RGBA"
 with Image.open(exported) as im:assert im.size==(1024,1024) and im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255)
 for ref in nr.get("references",[]):
  path=Path(ref.get("path","")).resolve()
  if path.is_relative_to(ROOT/"runtime"):
   old=Path(str(path)+".generation.json")
   saved=archive/str(old.relative_to(ROOT/"runtime")).replace("\\","--").replace("/","--")
   if saved.exists():
    ref["originalGenerationRecordPath"]=ref.get("generationRecord",str(old))
    ref["generationRecord"]=saved.relative_to(ROOT).as_posix()
    ref["generationRecordSha256"]=sha(saved)
 nr["review"]={"status":"selected_after_static_grounding_review","dynamicAcceptance":False,"reason":fix.get("reason","连续接地/靴轴局部修正")}
 wr(nrpath,nr)
 er["derivedFrom"]={"file":native.relative_to(ROOT).as_posix(),"sha256":sha(native),"generationRecord":nrpath.relative_to(ROOT).as_posix(),"generationRecordSha256":sha(nrpath)}
 wr(erpath,er)
 prior={"file":row["source"],"sha256":row["sourceSha256"],"generationRecord":(archive/str(Path(row["generationRecord"]).relative_to("runtime")).replace("\\","--").replace("/","--")).relative_to(ROOT).as_posix(),"nativeOrigin":row.get("nativeOrigin")}
 prior["generationRecordSha256"]=sha(ROOT/prior["generationRecord"])
 origin={**er["derivedFrom"],"nativeSize":[nr.get("width",1254),nr.get("height",1254)]}
 shutil.copyfile(exported,target)
 final={**er,"file":row["source"],"sha256":sha(target),"status":"offline_delivery_grounding_revision","nativeOrigin":origin,"priorFrame":prior,"visualReview":"static_grounding_reviewed","dynamicReview":"pending_new_browser_review","clientIntegration":"not_integrated","userFinalAcceptance":False}
 wr(ROOT/row["generationRecord"],final)
 row.update(sourceSha256=sha(target),nativeOrigin=origin,priorFrame=prior,nativeSize=origin["nativeSize"],inputIsFinalExport=True,visualReview="static_grounding_reviewed",dynamicReview="pending_new_browser_review",groundingRevision="2026-10-04")
 applied.append({**fix,"prior":prior,"runtime":row["source"],"sha256":sha(target)})
sel["updatedAt"]=datetime.now(ZoneInfo("America/New_York")).isoformat();wr(ROOT/"selection.json",sel)
wr(ROOT/"provenance/grounding4-applied.json",{"time":sel["updatedAt"],"replacements":applied,"retainedRuntimeSprites":196-len(applied),"clientIntegrated":False})
print(json.dumps({"replaced":len(applied),"retained":196-len(applied)},ensure_ascii=False))

