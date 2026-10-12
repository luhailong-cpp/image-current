from PIL import Image, ImageDraw
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
for d in ['N','W','NW']:
    canvas=Image.new('RGB',(1600,490),(226,229,227));draw=ImageDraw.Draw(canvas)
    chosen=[]
    for i in range(1,17):
        c=sorted((R/'work/grounding-v2/north'/d).glob(f'grounding-v3-{d}{i:02}-a[0-9][0-9].png'))
        p=c[-1] if c else R/f'frames/run/{d}/{i:02}.png'
        if d=='NW' and i in (2,3):p=R/f'frames/run/{d}/{i:02}.png'
        im=Image.open(p).convert('RGBA').resize((200,200))
        x=((i-1)%8)*200;y=((i-1)//8)*245
        canvas.paste(im,(x,y+25),im);draw.text((x+5,y+4),f'{d}{i:02} '+('NEW' if 'work' in str(p.relative_to(R)) else 'old'),fill=(20,30,30))
        chosen.append(str(p.relative_to(R)))
    canvas.save(R/f'reviews/finish-north-{d}-contact.jpg',quality=92)
    (R/f'reviews/finish-north-{d}-selection.json').write_text(json.dumps(chosen,indent=2),encoding='utf-8')
