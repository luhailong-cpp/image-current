"""Register one real built-in output; optional uniform whole-canvas export."""
import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def local(p):
    p = (ROOT / p).resolve()
    if not p.is_relative_to(ROOT): raise ValueError("outside character directory")
    return p
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
a=argparse.ArgumentParser()
a.add_argument("--native", required=True)
a.add_argument("--direction", required=True, choices=["W","N","NE","NW"])
a.add_argument("--frame", required=True, type=int)
a.add_argument("--attempt", required=True, type=int)
a.add_argument("--reject", action="store_true")
a.add_argument("--replace", action="store_true", help="replace this exact slot after visual review; retain old provenance")
args=a.parse_args()
if not 1 <= args.frame <= 16: raise ValueError("invalid frame")
stem=f"run-{args.direction}-{args.frame:02d}-attempt-{args.attempt:02d}"
record_path=local(f"records/{stem}.json")
record=json.loads(record_path.read_text(encoding="utf-8-sig"))
source=Path(args.native).resolve()
native_path=local(f"work/run-{args.direction}/{args.frame:02d}-attempt-{args.attempt:02d}-native.png")
native_path.parent.mkdir(parents=True,exist_ok=True)
if native_path.exists() and sha(native_path) != sha(source):
    raise ValueError("native path collision: existing SHA differs from actual host result; use a new unused attempt record, never reuse the existing file")
if not native_path.exists(): shutil.copy2(source,native_path)
im=Image.open(native_path);im.load()
if im.mode!="RGBA" or im.width!=im.height or min(im.size)<1024: raise ValueError("native must be square RGBA >=1024")
alpha=im.getchannel("A")
if alpha.getextrema() != (0,255): raise ValueError("actual alpha extrema not 0/255")
record["configSnapshot"]=json.loads((PROJECT/"config/image-generation.json").read_text(encoding="utf-8-sig"))
record["references"]=[{"path":p,"sha256":sha(Path(p))} for p in record["submittedParameters"]["referenced_image_paths"]]
record["native"]={"file":native_path.relative_to(ROOT).as_posix(),"sha256":sha(native_path),"width":im.width,"height":im.height,"mode":im.mode,"format":"PNG","alphaExtrema":list(alpha.getextrema()),"alphaBBoxDiagnosticOnly":alpha.getbbox()}
record["hostNativeVerification"]={"hostPath":str(source),"hostSha256":sha(source),"nativeSha256":sha(native_path),"match":sha(source)==sha(native_path)}
record["registeredAt"]=datetime.now(ZoneInfo("America/New_York")).isoformat()
record["timeZone"]="America/New_York"
record["prompt"]=f"prompts/{stem}.txt"
ended=record.get("endedAt",{}).get("current_time")
if ended:
    record["generatedAt"]=datetime.strptime(ended,"%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York")).isoformat()
record["actualModel"]=None;record["actualQuality"]=None
if args.reject:
    record["status"]="rejected"
    write(record_path,record)
    print(json.dumps({"status":"rejected","file":str(native_path)}));raise SystemExit(0)
dest=local(f"frames/run/{args.direction}/{args.frame:02d}.png")
if dest.exists():
    if not args.replace: raise ValueError("refuse overwrite formal frame without --replace")
    previous_sidecar=json.loads(dest.with_suffix(".png.generation.json").read_text(encoding="utf-8-sig"))
    record["replaces"]={"file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"generationRecord":previous_sidecar.get("generationRecord"),"reason":"new independent AI redraw selected after visible pose inspection; earlier generation provenance retained"}
dest.parent.mkdir(parents=True,exist_ok=True)
im.resize((1024,1024),Image.Resampling.LANCZOS).save(dest)
record["status"]="exported_candidate_pending_sequence_review"
record["export"]={"file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"size":[1024,1024],"mode":"RGBA","operation":"uniform full-canvas downsample; no crop, bbox scaling, translation, mirror, pose interpolation or alpha replacement","derivedFrom":record["native"]}
write(record_path,record)
write(dest.with_suffix(".png.generation.json"),{"file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"generationRecord":record_path.relative_to(ROOT).as_posix(),"derivedFrom":record["native"],"operation":record["export"]["operation"],"actualModel":None,"actualQuality":None})
inventory_path=local("inventory-run-north.json")
inv=json.loads(inventory_path.read_text(encoding="utf-8-sig")) if inventory_path.exists() else {"root_anchor":[512,920],"root_anchor_status":"prompt target only; global visual registration pending","directions":["W","N","NE","NW"],"expected_frames":64,"frames":[]}
inv["frames"]=[f for f in inv["frames"] if not (f["direction"]==args.direction and f["frame"]==args.frame)]
inv["frames"].append({"action":"run","direction":args.direction,"frame":args.frame,"path":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"native_size":[im.width,im.height],"native_evidence":record_path.relative_to(ROOT).as_posix(),"visual_status":record.get("visualQA",{}).get("status","pending_review")})
inv["frames"].sort(key=lambda f:(f["direction"],f["frame"]))
write(inventory_path,inv)
print(json.dumps({"status":record["status"],"file":str(dest),"native":[im.width,im.height],"sha256":sha(dest)}))
