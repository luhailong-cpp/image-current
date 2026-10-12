from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import base64, io, json

root = Path('E:/work/image/designs/attribute-panels/v2-painted/unity-slices')
items = [{'name': p.stem} for p in sorted((root/'png').glob('*.png'))]
font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
w,h=1440,((len(items)+3)//4)*196
sheet=Image.new('RGB',(w,h),'#243e35'); d=ImageDraw.Draw(sheet)
for i,e in enumerate(items):
    x=(i%4)*360;y=(i//4)*196
    d.rectangle((x+6,y+6,x+354,y+190),fill='#627169')
    d.text((x+15,y+12),e['name'],font=font,fill='#ffffff')
    for yy in range(y+42,y+182,14):
        for xx in range(x+12,x+348,14):
            d.rectangle((xx,yy,xx+13,yy+13), fill=('#c5ccc6' if ((xx-x)//14+(yy-y)//14)%2 else '#ece9df'))
    im=Image.open(root/'png'/f"{e['name']}.png").convert('RGBA')
    im.thumbnail((320,132),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+180-im.width//2,y+112-im.height//2),im)
sheet.save(root/'sprite-overview.png')
b=io.BytesIO();sheet.save(b,format='JPEG',quality=90)
print(base64.b64encode(b.getvalue()).decode())
