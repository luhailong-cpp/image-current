from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy")
keys=["attack-W-01-v2","attack-W-02-v4","attack-W-03-v4","attack-W-04-v2","attack-W-05-v2","attack-W-06-v2","attack-W-07-v1","attack-W-08-v1","attack-W-09-v1","attack-W-10-v2","attack-W-11-v1","attack-W-12-v2"]
out=Image.new("RGB",(1536,1290),(220,226,233));d=ImageDraw.Draw(out)
f=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",18)
for i,k in enumerate(keys):
 im=Image.open(B/"sources/new"/(k+".png")).convert("RGBA");im.thumbnail((384,384))
 x=i%4*384;y=i//4*430;out.paste(im,(x,y),im);d.text((x+10,y+390),k,font=f,fill=(15,20,30))
(B/"review/diagonals").mkdir(parents=True,exist_ok=True)
out.save(B/"review/diagonals/attack-W-inventory.png")

