from PIL import Image,ImageDraw
from pathlib import Path
base=Path(__file__).resolve().parents[2]
qa=base/'QA'/'attack'
qa.mkdir(parents=True,exist_ok=True)
for action,direction,n in [('hit','E',6),('hit','W',6),('attack','E',12),('attack','W',6)]:
    rows=(n+2)//3
    out=Image.new('RGB',(1536,rows*552),(230,233,230))
    d=ImageDraw.Draw(out)
    for j in range(n):
        p=base/'runtime'/action/direction/f'{j+1:02}.png'
        if not p.exists():continue
        with Image.open(p) as src:
            im=src.convert('RGBA');im.thumbnail((512,512))
            x=(j%3)*512;y=(j//3)*552
            out.paste(im,(x,y),im);d.text((x+12,y+518),f'{action} {direction}{j+1:02}',fill=(10,30,20))
    out.save(qa/f'{action}-{direction}-review.jpg',quality=92)

