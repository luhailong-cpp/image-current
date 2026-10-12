import argparse, hashlib, json, os, uuid, msvcrt
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex+'.tmp')
 tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
 os.replace(tmp,p)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument("mode",choices=["prepare","register"])
p.add_argument("--action",required=True)
p.add_argument("--frame",required=True,type=int)
p.add_argument("--direction",default="E")
p.add_argument("--native")
p.add_argument("--request")
p.add_argument("--receipt")
a=p.parse_args()
slot=f"{a.action}-{a.direction}-{a.frame:02d}"
group_name=("run-" if a.action=="run" else "combat-")+a.direction
if a.mode=="prepare":
 plan=read(REPO/"combat-20260929/characters/09_bamboo_archer_girl/production/animation-plan.json") if False else read(ROOT.parents[2]/"combat-20260929/characters/09_bamboo_archer_girl/production/animation-plan.json")
 group=next(g for g in plan["groups"] if g["action"]==a.action and g["direction"]=="E")
 frame=next(f for f in group["frames"] if f["frame"]==a.frame)
 prompt=f"""Use case: identity-preserve. Asset: ONE independently painted 1024x1024 transparent RGBA game animation frame, {slot}. Image1 exact identity EAST-facing camera and scale reference; image2 primary approved painting-style reference only, do not reproduce UI. If image3 present it is an adjacent accepted pose to maintain proportions and palette. Draw THIS pose independently, not copy image3.
Same brown high ponytail, bamboo-leaf gold jade hair ornament, green eyes, ivory jade-green gold embroidered short robe, white shorts, short boots, jade tassels, yin-yang belt. Same bright clean rounded chibi hand-painted detail, not plastic.
Face screen RIGHT with exactly image1 side-three-quarter camera and head/body scale. Anatomical LEFT hand holds one complete long bamboo bow, RIGHT hand does the action, quiver permanently anatomical RIGHT shoulder. Preserve non-symmetric features.
Frame phase: {frame["phase"]}. Required pose: {frame["pose"]}
Change from previous: {frame["deltaFromPrevious"]}
Transition to next: {frame["transitionToNext"]}
Use real shoulder elbow wrist and hip knee ankle articulation. Entire bow/string, hands, hair and boots within canvas. Clean natural fingers wrapped around grip, no floating hand, no limb fusion. Target in screen right. Fixed normalized virtual ground y=940/1024, pelvis x=600/1024; no camera changes, no overall horizontal translation, no independent bbox scaling. Keep same figure scale and ample transparent margins.
No background, floor, shadow, text, UI, sheet, grid, particles, halo, motion blur, detached projectiles, injury marks, extra limbs or weapons. During hit no arrow in hand. During attack/cast arrow only when physically nocked before release; after release remove arrow, no trail. True transparency; no red, magenta or yellow fringe around contour. Highest detail and finish."""
 refs=["D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/09-delivery-preview/final/runtime/idle/E.png","D:/work/image/designs/jubaozhai-ui/02-characters.png"]
 if a.action=="hit" and a.frame in [4,5,6]:
  refs.append(str(ROOT/"runtime/hit/E/03.png"))
  prompt += "\nImage3 is the established peak recoil frame03. Keep both planted boots at EXACT same screen positions and the same boot size as image3; recover through hips, knees, chest and shoulders only. Keep the same bow ornament positions/design and whole-body canvas scale."
 if (a.action=="attack" and a.frame in [4,5,6]) or (a.action=="cast" and a.frame in [5,6,7,8,9]):
  prompt += "\nPrecise archery mechanics: exactly one straight physical bamboo arrow points screen RIGHT. Its tip projects past bow grip; its rear nock is seated at the SAME point as right fingertips on the string. The bowstring is two taut straight segments from upper tip to the nock/right fingertips, and from that nock to the lower tip, a single clear V when drawn. No extra vertical undrawn string behind it. RIGHT elbow points back screen LEFT, left hand holds bow grip only, arrow rests just above left thumb. Arrow, nock, right fingertips and string apex form ONE mechanically connected system."
 args={"prompt":prompt,"referenced_image_paths":refs,"transparent_background":True}
 out=ROOT/"provenance/combat-E"/(slot+".request.json")
 attempt=1
 while out.exists():
  attempt+=1;out=ROOT/"provenance/combat-E"/(slot+f".a{attempt:02d}.request.json")
 write(out,{"slot":slot,"requestedAt":datetime.now(timezone.utc).isoformat(),"configSnapshot":read(ROOT.parents[3]/"config/image-generation.json"),"submittedParameters":{"model":None,"quality":None,**args},"referenceMetadata":[{"path":v,"sha256":sha(v)} for v in refs],"framePlan":frame})
 (out.parent/(slot+".prompt.txt")).write_text(prompt,encoding="utf-8")
 print(json.dumps({"request":str(out),"args":args},ensure_ascii=False))
else:
 native=Path(a.native);request=read(a.request);receipt=read(a.receipt)
 out=ROOT/"runtime"/a.action/a.direction/f"{a.frame:02d}.png";out.parent.mkdir(parents=True,exist_ok=True)
 im=Image.open(native);im.load();size=im.size
 if min(size)<1024: raise ValueError("native smaller than 1024")
 if im.mode!="RGBA": raise ValueError("native has no RGBA")
 alpha=im.getchannel("A")
 if alpha.getextrema()[0]==255: raise ValueError("native opaque")
 arr=np.asarray(im).copy(); noise=arr[:,:,3]<=2; removed=int(((arr[:,:,3]>0)&noise).sum()); arr[noise]=0
 clean=Image.fromarray(arr).resize((1024,1024),Image.Resampling.LANCZOS)
 arr=np.asarray(clean).copy(); arr[arr[:,:,3]<=2]=0
 Image.fromarray(arr).save(out)
 now=datetime.now(timezone.utc).isoformat()
 rec=out.with_suffix(".png.generation.json")
 promptpath=Path(a.request).with_suffix(".prompt.txt")
 config=request.get("configSnapshot") or read(ROOT.parents[3]/"config/image-generation.json")
 record={"file":str(out),"sha256":sha(out),"generatedAt":receipt.get("returnedAt",now),"exportedAt":now,"tool":"image_gen.imagegen","route":"builtin_host_managed_then_whole_canvas_export","configSnapshot":config,"submittedParameters":request["submittedParameters"],"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露实际型号/质量，无model或quality选择器。","width":1024,"height":1024,"format":"PNG","nativeSize":list(size),"nativeCellSize":list(size),"evidence":{"request":str(a.request),"receipt":str(a.receipt)},"prompt":request["submittedParameters"]["prompt"],"references":[{"path":v,"role":"identity_camera" if i==0 else "approved_primary_style","sha256":sha(v)} for i,v in enumerate(request["submittedParameters"]["referenced_image_paths"])],"derivedFrom":{"file":str(native),"sha256":sha(native),"nativeSize":list(size)},"operation":{"type":"whole_canvas_downsample","size":[1024,1024],"scale":[1024/size[0],1024/size[1]],"translation":[0,0],"bboxScaling":False,"lowestFootAlignment":False,"mirrored":False,"interpolated":False},"visualReview":"pending"}
 if request.get("referenceMetadata"):record["references"]=request["referenceMetadata"]
 record["operation"]["alphaNoiseCleanup"]={"thresholdInclusive":2,"nativeNonzeroAlphaPixelsRemoved":removed,"transparentRgbZeroed":True,"highAlphaColorChanged":False}
 if rec.exists():
  prior=read(rec)
  write(ROOT/"provenance"/group_name/"history"/(slot+"-"+prior["sha256"][:12]+".generation.json"),prior)
 write(rec,record)
 matches=[]
 for candidate in (ROOT/"selection").glob("*.json"):
  candidate_data=read(candidate)
  if any(f.get("action",candidate_data.get("action"))==a.action and f.get("direction",candidate_data.get("direction"))==a.direction and f.get("frame")==a.frame for f in candidate_data.get("frames",[])):
   matches.append(candidate)
 if len(matches)>1:raise ValueError(f"Multiple selections for {slot}: {matches}")
 sel=matches[0] if matches else ROOT/"selection"/(group_name+".json")
 with open(sel.with_suffix('.json.lock'),'a+b') as lock:
  lock.seek(0,os.SEEK_END)
  if lock.tell()==0:lock.write(b'0');lock.flush()
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
  try:
   data=read(sel) if sel.exists() else {"frames":[]}
   data["frames"]=[f for f in data["frames"] if not (f.get("action",data.get("action"))==a.action and f.get("direction",data.get("direction"))==a.direction and f["frame"]==a.frame)]
   data["frames"].append({"action":a.action,"direction":a.direction,"frame":a.frame,"file":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"generationRecord":rec.relative_to(ROOT).as_posix(),"generationRecordSha256":sha(rec),"sourceNativeSize":list(size)})
   write(sel,data)
  finally:
   lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
 print(json.dumps({"file":str(out),"sha256":sha(out),"nativeSize":size},ensure_ascii=False))


