import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",18)
groups=[(a,d,n,ms) for a,n,ms in [("hit",6,40),("attack",12,30),("cast",16,45)] for d in ["E","W"]]+[("run",d,16,75) for d in ["N","NE","E","SE","S","SW","W","NW"]]
for a,d,n,ms in groups:
 if len(sys.argv)>1 and f"{a}/{d}" not in sys.argv[1:]:continue
 files=[ROOT/"runtime"/a/d/f"{i:02d}.png" for i in range(1,n+1)]
 available=[(i+1,p) for i,p in enumerate(files) if p.exists()]
 if not available:continue
 cols=4; rows=(n+cols-1)//cols; tile=256
 contact=Image.new("RGB",(cols*tile,rows*(tile+26)),(241,239,229));draw=ImageDraw.Draw(contact)
 sources=[]
 for i,p in available:
  im=Image.open(p).convert("RGBA"); thumb=im.resize((tile,tile),Image.Resampling.LANCZOS)
  x=((i-1)%cols)*tile;y=((i-1)//cols)*(tile+26)
  contact.paste(thumb,(x,y),thumb);draw.text((x+8,y+tile),f"{a}/{d}/{i:02d}",font=font,fill=(28,60,47))
  sources.append({"file":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
 for i,p in enumerate(files,1):
  if p.exists():continue
  x=((i-1)%cols)*tile;y=((i-1)//cols)*(tile+26)
  draw.text((x+30,y+120),f"{i:02d} MISSING",font=font,fill=(150,100,90))
 out=ROOT/"preview"/"qa";out.mkdir(exist_ok=True)
 contact.save(out/f"{a}-{d}-contact.png")
 if len(available)==n:
  frames=[]
  for _,p in available:
   im=Image.open(p).convert("RGBA").resize((512,512),Image.Resampling.LANCZOS)
   bg=Image.new("RGB",(512,512),(235,237,228));bg.paste(im,(0,0),im);frames.append(bg)
  timings=[("normal",[40,50]*(n//2) if ms==45 else ms),("slow",ms*4)]

  for speed,duration in timings:
   if a=="run":
    frames[0].save(out/f"{a}-{d}-{speed}.apng",format="PNG",save_all=True,append_images=frames[1:],duration=duration,loop=0,disposal=0,blend=0)
   else:
    frames[0].save(out/f"{a}-{d}-{speed}.gif",save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False,disposal=2)
 (out/f"{a}-{d}-preview.sources.json").write_text(json.dumps({"operation":"whole-canvas scaled display and background composite; previews only","sources":sources,"complete":len(available)==n,"intendedMsPerFrame":ms,"runTimingStatus":"1200ms / uniform75ms applied to preview; client unchanged" if a=="run" else None,"note":"Run APNG and HTML use exact75ms; run slow300ms. Combat GIF45ms uses alternating40/50ms, unchanged. No frame duplication, interpolation, root shift or automatic approval."},indent=2),encoding="utf-8")
print("Review previews updated without altering runtime PNG.")

