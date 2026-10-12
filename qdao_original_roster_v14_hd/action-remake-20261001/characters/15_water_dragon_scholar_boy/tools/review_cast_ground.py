from pathlib import Path
from PIL import Image,ImageDraw
b=Path(__file__).resolve().parents[1]
keys=['cast-E-05-foot-v1','cast-E-06-ground-v3','cast-E-07-ground-v4','cast-E-08-foot-v1','cast-E-09-ground-v1','cast-E-10-foot-v1']
sheet=Image.new('RGB',(1254,keys.__len__()*314),(28,37,48));dr=ImageDraw.Draw(sheet)
for i,key in enumerate(keys):
 im=Image.open(b/'sources/new'/f'{key}.png').convert('RGBA')
 crop=im.crop((0,960,1254,1254))
 sheet.paste(crop,(0,i*314+20),crop)
 dr.text((8,i*314+4),key,fill='white')
 for x in [320,525,820,1040]:dr.line((x,i*314+20,x,i*314+313),fill=(60,120,145),width=2)
 dr.line((0,i*314+250,1254,i*314+250),fill=(160,115,50),width=2)
sheet.save(b/'audit/cast-E-ground-contact.png')
print('diagnostic crop created')

