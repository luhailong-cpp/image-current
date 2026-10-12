from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/16-luhualing")
reasons={"02":"Rejected: original pot-side and branch-side arms swapped; replaced by third candidate.","05":"Rejected: unnecessary detached petals during physical attack; replaced with clean candidate.","06":"Rejected: unnecessary green glow/ribbon and petals; replaced with clean candidate.","07":"Rejected: release twig trajectory rose toward horizontal after downward-right approach; replaced with down-right thrust.","08":"Rejected candidate: first excessive glowing vortex; second raised wrist trajectory. Final replacement has clean downward-right follow-through."}
for p in (root/"records/attack/E").glob("*.rejected-*.generation.json"):
 d=json.loads(p.read_text(encoding="utf-8"))
 frame=p.name[:2]; idx=p.name.split(".rejected-")[1].split(".")[0]
 d["file"]=None
 d["sourceFile"]=None
 d["candidateDisposition"]="rejected_source_overwritten_in_workspace"
 d["rejectionReason"]=reasons[frame]
 d["prompt"]=f"prompts/attack/E{frame}.rejected-{idx}.txt"
 d["evidence"]["receipt"]=f"records/attack/E{frame}.rejected-{idx}.receipt.json"
 d["visualStatus"]="rejected"
 d["exportStatus"]="do_not_export"
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for direction,count in [("E",12),("W",8)]:
 canvas=Image.new("RGB",(1280,((count+3)//4)*344),(37,44,47))
 draw=ImageDraw.Draw(canvas)
 for n in range(1,count+1):
  p=root/".work/attack"/direction/f"{n:02}.png"
  im=Image.open(p).convert("RGBA").resize((320,320),Image.Resampling.LANCZOS)
  x=(n-1)%4*320;y=(n-1)//4*344
  canvas.paste(im,(x,y),im)
  draw.text((x+10,y+324),f"attack {direction} {n:02}",fill=(255,255,255))
 out=root/"records/attack"/f"review-{direction}.jpg"
 canvas.save(out,quality=95)
 print(out)


