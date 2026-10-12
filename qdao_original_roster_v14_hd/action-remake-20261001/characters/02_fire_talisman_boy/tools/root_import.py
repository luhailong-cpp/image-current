from pathlib import Path
import argparse, json, hashlib, shutil
from datetime import datetime, timezone, timedelta
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def local(p):
    p=(ROOT/p).resolve()
    if not p.is_relative_to(ROOT.resolve()): raise ValueError("outside role directory")
    return p
a=argparse.ArgumentParser()
a.add_argument("--native",required=True)
a.add_argument("--action",required=True,choices=["attack","run"])
a.add_argument("--direction",required=True,choices=["E","W","SE"])
a.add_argument("--frame",required=True,type=int)
a.add_argument("--record",required=True)
a.add_argument("--review",default="key_pose_reviewed_sequence_pending")
a.add_argument("--replace",action="store_true")
args=a.parse_args()
source=Path(args.native).resolve()
im=Image.open(source)
if im.mode!="RGBA" or min(im.size)<1024 or im.width!=im.height: raise ValueError("native must be square RGBA >=1024")
native_size=list(im.size)
dest=local(Path("frames")/args.action/args.direction/f"{args.frame:02}.png")
dest.parent.mkdir(parents=True,exist_ok=True)
previous = None
if dest.exists():
    if not args.replace: raise ValueError("do not overwrite existing frame")
    previous = {"file":str(dest.relative_to(ROOT)),"sha256":sha(dest),"reason":"superseded by targeted AI pose/registration repair"}
im.resize((1024,1024),Image.Resampling.LANCZOS).save(dest)
out=Image.open(dest)
recordp=local(args.record)
record=json.loads(recordp.read_text(encoding="utf-8-sig"))
for ref in record.get("references",[]):
    refpath=Path(ref["path"])
    if not ref.get("sha256") and refpath.is_file():
        ref["sha256"] = previous["sha256"] if previous and refpath.resolve() == dest.resolve() else sha(refpath)
if previous: record["supersedes"]=previous
record.update(status="exported_candidate", actualModel=None,actualQuality=None,importedAt=datetime.now(timezone(timedelta(hours=-4))).isoformat(),generatedAt=datetime.fromtimestamp(source.stat().st_mtime,timezone(timedelta(hours=-4))).isoformat(),generatedAtEvidence="native file last-write time observed at import; not a returned server timestamp",native={"sourceFile":str(source),"width":native_size[0],"height":native_size[1],"mode":im.mode,"sha256":sha(source)},export={"file":str(dest.relative_to(ROOT)).replace("\\","/"),"sha256":sha(dest),"width":1024,"height":1024,"mode":"RGBA","operation":"uniform full-canvas downsample only; no bbox registration, mirror, warp or interpolation of poses","nativeSize":native_size},unverifiedReason="宿主管理，工具未披露实际型号/质量；PNG无可确认型号/质量元数据。")
record.setdefault("evidence",{})
record["evidence"].update(importSourcePath=str(source),modelReturned=False,qualityReturned=False)
if not record.get("recovery"): record["evidence"]["toolResultKeys"]=["image_url","output_hint"]
recordp.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
sidecar=dest.with_suffix(".png.generation.json")
sidecar.write_text(json.dumps({"file":str(dest.relative_to(ROOT)).replace("\\","/"),"sha256":sha(dest),"derivedFrom":{"sha256":sha(source),"generationRecord":str(recordp.relative_to(ROOT)).replace("\\","/"),"nativeSize":native_size},"operation":"uniform full-canvas downsample to 1024x1024 RGBA","actualModel":None,"actualQuality":None},ensure_ascii=False,indent=2),encoding="utf-8")
invpath=local("inventory-root.json")
inv=json.loads(invpath.read_text(encoding="utf-8")) if invpath.exists() else {"root_anchor":[512,920],"frames":[]}
if args.replace: inv["frames"]=[f for f in inv["frames"] if (f["action"],f["direction"],f["frame"])!=(args.action,args.direction,args.frame)]
inv["frames"].append({"action":args.action,"direction":args.direction,"frame":args.frame,"path":str(dest.relative_to(ROOT)).replace("\\","/"),"native_size":native_size,"native_evidence":str(recordp.relative_to(ROOT)).replace("\\","/"),"sha256":sha(dest),"visual_status":args.review})
inv["frames"].sort(key=lambda x:(x["action"],x["direction"],x["frame"]))
invpath.write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":str(dest),"sha256":sha(dest),"native_size":native_size,"alpha_extrema":out.getchannel("A").getextrema()},ensure_ascii=False))

