import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for action,count in [("hit",6),("attack",12)]:
 for n in range(1,count+1):
  out=root/"runtime"/action/"E"/f"{n:02d}.png"
  p=Path(str(out)+".generation.json")
  r=json.loads(p.read_text(encoding="utf-8"))
  r["action"]=action;r["direction"]="E";r["frame"]=n
  r["durationMs"]=40 if action=="hit" else 30;r["pivot"]=[.5,.08]
  r["event"]=("impact" if action=="hit" else "attack") if n==(3 if action=="hit" else 7) else None
  r["visualReview"]={"status":"reviewed-native-and-export-contact-sheet","reviewedAt":datetime.now(timezone.utc).isoformat(),"checks":["E front three-quarter lower-right","two arms and two legs","anatomical right-hand fan with three bells","left empty hand","preserved short black bob and folded-petal costume","full silhouette","ordered pose progression and recovery reviewed as stills"],"sequence":"continuous-playback-not-observed"}
  for ref in r["references"]:
   if not ref.get("sha256") and Path(ref["path"]).is_file():ref["sha256"]=sha(Path(ref["path"]))
  p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
  files.append(r["file"])
rejected=root/"records"/"hit-E-04-attempt1.json"
r=json.loads(rejected.read_text(encoding="utf-8"))
r.update(disposition="rejected-superseded",rejectedReason="left arm returned to rest too early; stray puff near tassel",prompt="prompts/hit-E-04-attempt1.txt")
r["evidence"]["receipt"]="receipts/hit-E-04-attempt1.json"
r["supersededBy"]="runtime/hit/E/04.png.generation.json"
rejected.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"qa"/"E-hit-attack-visual.json").write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),files=files,stillReview="reviewed",continuousPlayback="not_observed",clientReview="not_tested",repair=dict(frame="hit/E/04",reason="premature left-arm rest and puff",result="replaced by independent AI repair")),ensure_ascii=False,indent=2),encoding="utf-8")
print(f"Updated visual records: {len(files)}")

