"""Record and export a single generated frame using fixed full-canvas downsampling.
Never aligns by bounding box or changes body proportions. All writes stay in this character.
"""
import argparse, hashlib, json, re, shutil
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(p):
 p=p.resolve()
 if not p.is_relative_to(ROOT.resolve()): raise ValueError("Write outside character rejected")
 return p
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("source"); ap.add_argument("stem"); ap.add_argument("prompt")
 ap.add_argument("--action"); ap.add_argument("--direction"); ap.add_argument("--frame",type=int)
 ap.add_argument("--review",default="pending")
 ap.add_argument("--generated-at")
 ap.add_argument("--references",help="JSON array of actual reference paths and roles")
 args=ap.parse_args()
 source=Path(args.source); dest=safe(ROOT/"work"/(args.stem+".png"))
 dest.parent.mkdir(parents=True,exist_ok=True)
 if source.resolve()!=dest: shutil.copy2(source,dest)
 im=Image.open(dest); im.load()
 refs=[
 ("q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png","authoritative identity"),
 ("qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/E.png","east camera/proportions"),
 ("qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/W.png","west camera/proportions"),
 ("designs/jubaozhai-ui/02-characters.png","approved primary painted style")]
 refs=[{"path":str(REPO/p),"role":role,"sha256":sha(REPO/p)} for p,role in refs]
 if args.references:
  refs=json.loads(Path(args.references).read_text(encoding="utf-8-sig"))
  refs=[{**r,"sha256":sha(Path(r["path"]))} for r in refs]
 raw=dest.read_bytes()
 strings=[s.decode("ascii",errors="replace") for s in re.findall(rb"[ -~]{8,}",raw[:100000]) if b"gpt-image" in s or b"ChatGPT" in s or b"2026-10" in s]
 try: now=datetime.now(ZoneInfo("America/New_York")).isoformat()
 except Exception: now=datetime.now(timezone.utc).isoformat()
 times=re.findall(rb"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z",raw[:100000])
 actual_time=args.generated_at or (times[0].decode() if times else None)
 record={"schema_version":1,"file":str(dest.relative_to(ROOT)).replace("\\","/"),"sha256":sha(dest),
 "generatedAt":actual_time,"recordedAt":now,"width":im.width,"height":im.height,"format":im.format,"mode":im.mode,
 "native":{"width":im.width,"height":im.height,"perFrameWidth":im.width,"perFrameHeight":im.height},
 "tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads((REPO/"config/image-generation.json").read_text(encoding="utf-8-sig")),
 "submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[r["path"] for r in refs]},
 "actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理；工具没有 model/quality 选择器，回执未披露实际版本或质量。C2PA 中通用 gpt-image 不能证明具体版本。",
 "evidence":{"hostOutputPath":str(source),"resultFields":["image_url","output_hint"],"c2paPrintableExcerpts":strings},
 "prompt":args.prompt,"references":refs,"visualReview":args.review,"exported":False}
 rec=safe(dest.with_name(dest.name+".generation.json"))
 rec.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 if args.action:
  if im.width<1024 or im.height<1024: raise ValueError("Native single-frame resolution below 1024")
  if im.width!=im.height: raise ValueError("Non-square native canvas requires explicit global-camera decision")
  if im.mode!="RGBA" or im.getchannel("A").getextrema()[0]!=0: raise ValueError("Native RGBA transparency check failed")
  out=safe(ROOT/"runtime"/args.action/args.direction/f"{args.frame:02d}.png")
  out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists(): raise FileExistsError(out)
  im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
  derived={"file":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"width":1024,"height":1024,"format":"PNG","mode":"RGBA",
  "derivedFrom":[{"file":record["file"],"sha256":record["sha256"],"generationRecord":rec.relative_to(ROOT).as_posix()}],
  "native":record["native"],"operation":"Full canvas uniform Lanczos downsample to 1024; no cropping, mirroring, warping or per-frame bbox alignment",
  "actualModel":None,"actualQuality":None,"unverifiedReason":record["unverifiedReason"],"visualReview":args.review,
  "anchor":{"type":"provisional fixed virtual ground/root","x":512,"y":942,"normalizedUnityPivot":[0.5,0.08],"verified":False},
  "generatedAt":actual_time}
  out.with_name(out.name+".generation.json").write_text(json.dumps(derived,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  record["exported"]=True; record["exportPath"]=out.relative_to(ROOT).as_posix()
  rec.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"file":record["file"],"size":im.size,"sha256":record["sha256"],"exported":record["exported"]},ensure_ascii=False))
if __name__=="__main__": main()

