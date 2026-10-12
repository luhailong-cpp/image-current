"""Make review-only full-canvas contact sheets; never change source PNG pixels."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
B=Path(__file__).resolve().parents[1]
selected={
 'W':[(1,2),(2,1),(3,2),(4,4),(9,5),(10,4),(11,6),(12,3)],
 'SE':[(1,3),(2,2),(3,2),(4,4),(9,4),(10,1),(11,1),(12,4)]}
for direction,versions in selected.items():
 canvas=Image.new('RGB',(1280,700),'#d9ddd6'); draw=ImageDraw.Draw(canvas)
 legs=Image.new('RGB',(1600,800),'#d9ddd6'); ld=ImageDraw.Draw(legs)
 for i,(frame,v) in enumerate(versions):
  name=f'run-{direction}-{frame:02d}-v{v}.png'
  im=Image.open(B/'staging'/name).convert('RGBA')
  thumb=im.resize((320,320),Image.Resampling.LANCZOS)
  x,y=i%4*320,i//4*350
  canvas.paste(thumb,(x,y),thumb); draw.text((x+8,y+325),name,fill='#17251d')
  crop=im.crop((200,790,1100,1254));crop.thumbnail((400,355))
  lx,ly=i%4*400,i//4*400
  legs.paste(crop,(lx,ly),crop);ld.text((lx+8,ly+370),name,fill='#17251d')
 canvas.save(B/'review'/f'contact-position-{direction}-240plus.jpg',quality=94)
 legs.save(B/'review'/f'contact-position-{direction}-legs.jpg',quality=96)
 print(direction)
