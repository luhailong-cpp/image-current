"""Promote 8 reviewed directional selections atomically with sources read before mutation."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,copy,io,argparse
ROOT=Path(__file__).resolve().parents[1]
DIRS=["N","NE","E","SE","S","SW","W","NW"]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def inside(s):
 p=(ROOT/s).resolve();assert p.is_relative_to(ROOT),p
 return p
def rel(p):return p.relative_to(ROOT).as_posix()
def archived(p):return ROOT/"provenance/grounding4-prior-records"/str(p.relative_to(ROOT/"runtime")).replace("\\","--").replace("/","--")
out=ROOT/"provenance/grounding-pairs-applied.json"
ap=argparse.ArgumentParser();ap.add_argument("--validate-available",action="store_true");args=ap.parse_args()
assert not out.exists(),"Already promoted; never silently reapply historical source paths."
sel=rd(ROOT/"selection.json");oldsel=copy.deepcopy(sel)
bykey={(f["action"],f["direction"],f["frame"]):f for f in sel["frames"]}
prepared=[];stamp=datetime.now(timezone.utc).isoformat()
# Validate and read ALL input bytes before writing any runtime sprite.
for d in DIRS:
 if args.validate_available and not (ROOT/f"grounding4/{d}/selected.json").exists():continue
 rows=rd(ROOT/f"grounding4/{d}/selected.json")
 assert len(rows)==16 and {int(r["frame"]) for r in rows}==set(range(1,17)),d
 assert all(r.get("visualStaticReviewed") for r in rows),f"{d} not reviewed"
 hashes=set()
 for s in rows:
  n=int(s["frame"]);p=inside(s["exportFile"]);raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
  assert h==s["sha256"],p
  assert h not in hashes,(d,n);hashes.add(h)
  im=Image.open(io.BytesIO(raw));assert im.mode=="RGBA" and im.size==(1024,1024) and im.getchannel("A").getextrema()==(0,255),p
  row=bykey[("run",d,n)];target=inside(row["source"])
  rp=inside(s["generationRecord"]);source_rec=rd(rp)
  is_runtime=p.is_relative_to(ROOT/"runtime")
  if is_runtime:
   assert h==source_rec["sha256"],p
   origin=copy.deepcopy(source_rec["nativeOrigin"])
   source_record_path=archived(rp)
   op=source_rec.get("operation",{})
  else:
   native=inside(s["nativeFile"]);nh=sha(native)
   with Image.open(native) as ni:
    assert min(ni.size)>=1024 and ni.mode=="RGBA"
    native_size=list(ni.size)
   # Records may describe native+export together or reference the native sidecar.
   known=source_rec.get("native",{}).get("sha256") or source_rec.get("nativeSha256") or source_rec.get("sha256")
   if rp==Path(str(native)+".generation.json"):assert known==nh
   elif source_rec.get("native") or source_rec.get("nativeSha256"):assert known==nh
   exprecpath=Path(str(p)+".generation.json");exprec=rd(exprecpath)
   eh=exprec.get("sha256") or exprec.get("export",{}).get("sha256") or exprec.get("exportSha256")
   assert eh==h,(p,eh,h)
   origin={"file":rel(native),"sha256":nh,"nativeSize":native_size,"generationRecord":rel(rp),"generationRecordSha256":sha(rp)}
   source_record_path=rp
   op=exprec.get("operation",exprec.get("export",{}).get("operation",exprec.get("transform",{})))
  prior_rp=inside(row["generationRecord"])
  prior={"file":row["source"],"sha256":row["sourceSha256"],"generationRecord":rel(archived(prior_rp)),"generationRecordSha256":sha(prior_rp),"nativeOrigin":row.get("nativeOrigin")}
  prepared.append({"selection":s,"row":row,"target":target,"raw":raw,"sha":h,"origin":origin,"source_record":source_record_path,"source_record_sha":sha(rp),"operation":op,"prior":prior,"same":p==target,"is_runtime":is_runtime,"source_path":rel(p)})
if args.validate_available:
 print(json.dumps({"validated":len(prepared),"directions":sorted({x['row']['direction'] for x in prepared})}));raise SystemExit(0)
assert len(prepared)==128
# Text archive is immutable; no image backup.
arc=ROOT/"provenance/grounding4-prior-records";arc.mkdir(exist_ok=True)
for p in (ROOT/"runtime").rglob("*.png.generation.json"):
 dest=archived(p)
 if dest.exists():assert dest.read_bytes()==p.read_bytes(),dest
 else:dest.write_bytes(p.read_bytes())
wr(ROOT/"provenance/grounding4-prior-selection.json",oldsel)
wr(ROOT/"provenance/grounding4-prior-review.json",rd(ROOT/"provenance/offline-visual-review.json"))
applied=[]
for item in prepared:
 s=item["selection"];row=item["row"];target=item["target"];runtime=rel(target)
 rec={"file":runtime,"sha256":item["sha"],"width":1024,"height":1024,"format":"PNG","mode":"RGBA",
 "derivedFrom":item["origin"],"nativeOrigin":item["origin"],"nativeSize":item["origin"]["nativeSize"],
 "sourceExport":{"file":item["source_path"],"sha256":item["sha"],"generationRecord":rel(item["source_record"]),"generationRecordSha256":item["source_record_sha"],"historicalAfterPromotion":True},
 "operation":item["operation"],"pivot":[512,922],"status":"offline_delivery","isNewAIGeneration":False,
 "modelAndQuality":"沿来源记录核实；宿主未披露实际型号/质量，不以目标配置冒充实际值",
 "actualModel":None,"actualQuality":None,"visualReview":"grounding_pairs_static_reviewed","dynamicReview":"pending_current_browser_review",
 "reviewRecord":"provenance/offline-visual-review.json","clientIntegration":"not_integrated","userFinalAcceptance":False,
 "groundingPairs":{"supportFoot":s["supportFoot"],"position":s["position"],"frame":s["frame"],"frameMs":75,"loopMs":1200},
 "priorFrame":item["prior"],"inputReferenceHistory":"provenance/grounding4-prior-records",
 "exportedAt":stamp}
 target.write_bytes(item["raw"]);wr(Path(str(target)+".generation.json"),rec)
 row.update(sourceSha256=item["sha"],nativeOrigin=item["origin"],nativeSize=item["origin"]["nativeSize"],generationRecord=runtime+".generation.json",inputIsFinalExport=True,status="offline_delivery",visualReview=rec["visualReview"],dynamicReview=rec["dynamicReview"],groundingRevision="2026-10-04_position_pairs",groundingPairs=rec["groundingPairs"],priorFrame=item["prior"])
 applied.append({"direction":row["direction"],"frame":row["frame"],"runtime":runtime,"sha256":item["sha"],"selectedSource":item["source_path"],"mode":"retained" if item["same"] else "rephased_existing" if item["is_runtime"] else "local_AI_edit","nativeOrigin":item["origin"],"prior":item["prior"]})
sel.update(updatedAt=stamp,status="offline_delivery",groundingRevision="2026-10-04_position_pairs",groundingSelectionPlanMeaning="grounding4/*/selected.json为本轮历史入选来源；当前成品以frames中的runtime路径与SHA为准")
sel["exportTransform"]={"pivot":[512,922],"canvas":[1024,1024],"method":"按每张图旁operation；旧成品保持原固定画布变换，新局部编辑按完整原生画布等比缩放1024","bboxScaling":False,"lowestPixelAlignment":False}
wr(ROOT/"selection.json",sel)
wr(out,{"time":stamp,"applied":applied,"count":len(applied),"counts":{m:sum(x["mode"]==m for x in applied) for m in ["retained","rephased_existing","local_AI_edit"]},"combatRetained":68,"clientIntegrated":False,"runtimeInputTextArchive":rel(arc)})
print(json.dumps({"promoted":len(applied),"modeCounts":rd(out)["counts"]},ensure_ascii=False))
