from pathlib import Path
from PIL import Image, ImageDraw,ImageFont
b=Path(__file__).resolve().parents[1]
keys=['01-v1','02-v1','03-v2','04-v2','04-v1','06-v1','07-v2','05-v1','09-v2','10-v2','11-v2','12-v1','13-v2','14-v2','15-v1','16-v1']
out=Image.new('RGB',(1600,1760),(210,215,222))
d=ImageDraw.Draw(out);f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for i,key in enumerate(keys):
 im=Image.open(b/'sources/new'/('run-W-'+key+'.png')).convert('RGBA');im=im.resize((400,400))
 x=i%4*400;y=i//4*440;out.paste(im,(x,y+40),im);d.text((x+8,y+8),f'{i+1:02d}: {key}',fill=(12,12,12),font=f);d.line((x,y+420,x+400,y+420),fill=(180,70,70),width=2)
out.save(b/'audit/run-W-inventory-contact.png')

