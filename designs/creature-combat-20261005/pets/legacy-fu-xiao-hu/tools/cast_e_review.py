from pathlib import Path
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parents[1]
nums=[5,6,7,14,15,16]
sheet=Image.new("RGB",(1536,1080),(65,79,78));d=ImageDraw.Draw(sheet)
for k,n in enumerate(nums):
 im=Image.open(base/"runtime"/"cast"/"E"/f"{n:02d}.png").convert("RGBA").resize((512,512),Image.Resampling.LANCZOS)
 x=(k%3)*512;y=(k//3)*540
 sheet.paste(im,(x,y+24),im);d.text((x+10,y+6),f"cast E {n:02d}",fill="white");d.line((x,y+24+478,x+511,y+24+478),fill=(121,142,135),width=1)
sheet.save(base/"records"/"cast-E-review-contact.png")
