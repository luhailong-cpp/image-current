from pathlib import Path
from PIL import Image,ImageDraw
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian")
sheet=Image.new("RGB",(1536,1664),(234,232,222))
dr=ImageDraw.Draw(sheet)
for n in range(1,17):
 im=Image.open(base/"runtime/cast/W"/f"{n:02d}.png").resize((384,384),Image.Resampling.LANCZOS)
 x=((n-1)%4)*384;y=((n-1)//4)*416
 sheet.paste(im,(x,y),im)
 dr.text((x+12,y+389),f"W CAST {n:02d} / 45 ms",fill=(32,48,44))
sheet.save(base/"provenance/cast/W/qa-contact-sheet.png")

