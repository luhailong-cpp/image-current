from pathlib import Path
from PIL import Image,ImageDraw
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy")
versions=[1,1,1,1,2,1,1,1,4,1,2,1,1,1,1,3]
canvas=Image.new("RGB",(960,1056),(218,218,218));d=ImageDraw.Draw(canvas)
for n,v in enumerate(versions,1):
 p=B/"staging"/f"run-NE-{n:02d}-v{v}.png"
 im=Image.open(p).convert("RGBA").resize((240,240),Image.Resampling.LANCZOS)
 x=((n-1)%4)*240;y=((n-1)//4)*264
 d.text((x+5,y+5),p.stem,fill=(0,0,0));canvas.paste(im,(x,y+24),im)
canvas.save(B/"review"/"run-NE-reference09-selected-contact.png")
print("created")

