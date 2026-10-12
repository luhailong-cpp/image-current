from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling");F=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",14)
frames=[("E",1),("E",6),("E",7),("E",8),("W",1)]
out=Image.new("RGB",(600*len(frames),300),(235,232,220));dr=ImageDraw.Draw(out)
for idx,(d,n) in enumerate(frames):
 im=Image.open(B/"runtime"/"attack"/d/f"{n:02d}.png").convert("RGBA").crop((250,800,850,1024))
 out.paste(im,(idx*600,40),im);dr.text((idx*600+10,5),f"{d}/{n:02d}: x=250..850, y=800..1024",font=F,fill=(0,0,0))
 for x in range(250,851,50):
  xx=idx*600+x-250;dr.line((xx,40,xx,264),fill=(175,187,190),width=1);dr.text((xx+2,266),str(x),font=F,fill=(15,30,35))
 for y in range(800,1025,25):
  yy=40+y-800;dr.line((idx*600,yy,idx*600+599,yy),fill=(175,187,190),width=1);dr.text((idx*600+2,yy+1),str(y),font=F,fill=(15,30,35))
out.save(B/"provenance"/"attack"/"static-review-foot-grid.png")

