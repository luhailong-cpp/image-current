from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
R=Path(__file__).resolve().parents[1]
O=R/'previews'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
sources=[]
for action in ['run','hit','attack','cast']:
    for d in sorted((R/'frames'/action).iterdir()):
        paths=sorted(d.glob('*.png'))
        cols=4;cell=280;top=44;rows=(len(paths)+3)//4
        out=Image.new('RGB',(cols*cell,rows*(cell+28)+top),'#edeadf')
        draw=ImageDraw.Draw(out)
        draw.text((12,12),f'02 FIRE TALISMAN BOY | {action} {d.name}',font=font,fill='#21443d')
        for i,p in enumerate(paths):
            x=i%cols*cell;y=i//cols*(cell+28)+top
            im=Image.open(p).resize((cell,cell),Image.Resampling.LANCZOS)
            out.paste(im,(x,y),im)
            draw.text((x+10,y+cell+2),p.stem,font=font,fill='#21443d')
            sources.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        out.save(O/f'{action}-{d.name}-contact.png')
directions=['N','NE','E','SE','S','SW','W','NW']
cards=[]
for n in range(1,17):
    card=Image.new('RGB',(1024,590),'#f5efdf');draw=ImageDraw.Draw(card)
    draw.text((16,12),'02 FIRE TALISMAN BOY | RUN 960 ms | 16 x 60 ms',font=font,fill='#23443c')
    for i,d in enumerate(directions):
        x=i%4*256;y=i//4*274+38
        im=Image.open(R/'frames'/'run'/d/f'{n:02}.png').resize((250,250),Image.Resampling.LANCZOS)
        card.paste(im,(x,y),im)
        draw.text((x+12,y+249),f'{d}  {n:02}/16',font=font,fill='#23443c')
    cards.append(card)
cards[0].save(O/'run-eight-directions.gif',save_all=True,append_images=cards[1:],duration=[60]*16,loop=0,disposal=2,optimize=False)
cards[7].save(O/'run-eight-directions.png')
(O/'contact-sources.json').write_text(json.dumps({'operation':'full-canvas preview reduction and layout only; original PNGs untouched','gifTiming':'GIF and HTML uniform60ms, total960','sources':sources},indent=2),encoding='utf-8')
print({'contacts':14,'preview_frames':len(cards),'source_frames':len(sources)})
