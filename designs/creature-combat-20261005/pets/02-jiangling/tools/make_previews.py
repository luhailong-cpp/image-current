from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
outputs=[]
for action,count,ms in [("hit",6,40),("attack",12,30),("cast",16,45)]:
 for direction in ["E","W"]:
  paths=[root/"runtime"/action/direction/f"{n:02d}.png" for n in range(1,count+1)]
  if not all(p.exists() for p in paths):continue
  frames=[]
  for n,p in enumerate(paths,1):
   canvas=Image.new("RGBA",(512,544),(241,237,224,255))
   d=ImageDraw.Draw(canvas)
   for y in range(0,512,32):
    for x in range(0,512,32):
     if (x//32+y//32)%2:d.rectangle((x,y,x+31,y+31),fill=(220,223,211,255))
   im=Image.open(p).convert("RGBA").resize((512,512),Image.Resampling.LANCZOS)
   canvas.alpha_composite(im,(0,0))
   d.text((12,519),f"Jiangling | {action} {direction} | {n:02d}/{count} | {ms}ms",fill=(26,73,62,255))
   frames.append(canvas.convert("RGB"))
  for name,scale in [("normal",1),("slow025",4)]:
   out=root/"previews"/f"{action}-{direction}-{name}.webp"
   out.parent.mkdir(exist_ok=True)
   frames[0].save(out,save_all=True,append_images=frames[1:],duration=ms*scale,loop=0,lossless=True,method=4)
   check=Image.open(out)
   outputs.append(dict(file=out.relative_to(root).as_posix(),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),frameCount=check.n_frames,durationMsPerFrame=ms*scale,operation="preview-only uniform resize 1024 to 512 and checkerboard composite; no runtime changes; no synthesized frames",derivedFrom=[dict(file=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]))
(root/"previews"/"generation.json").write_text(json.dumps(dict(builtAt=datetime.now(timezone.utc).isoformat(),tool="Pillow export only",outputs=outputs),ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(dict(animatedPreviews=len(outputs),groups=len(outputs)//2)))

