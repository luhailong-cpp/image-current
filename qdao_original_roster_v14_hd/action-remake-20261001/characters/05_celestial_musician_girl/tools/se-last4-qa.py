from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'provenance/ground-contact-20261004'
items=[('13 v4','staging/run/SE/ground-13-v4.png'),('14 v7','staging/run/SE/ground-14-v7.png'),('15 v9','staging/run/SE/ground-15-v9.png'),('16 v9','staging/run/SE/ground-16-v9.png'),('01 next','final/run/SE/01.png')]
for kind in ['full','feet']:
    w,h=(256,292) if kind=='full' else (400,300)
    sheet=Image.new('RGB',(w*5,h),'#343840'); draw=ImageDraw.Draw(sheet)
    for i,(label,p) in enumerate(items):
        im=Image.open(ROOT/p).convert('RGBA')
        if kind=='feet': im=im.crop((270,715,850,1024))
        im.thumbnail((w,h-30),Image.Resampling.LANCZOS)
        sheet.paste(im,(i*w+(w-im.width)//2,30),im)
        draw.text((i*w+10,8),label,fill='white')
    sheet.save(OUT/f'SE-last4-{kind}.jpg',quality=95)
print('QA saved')

