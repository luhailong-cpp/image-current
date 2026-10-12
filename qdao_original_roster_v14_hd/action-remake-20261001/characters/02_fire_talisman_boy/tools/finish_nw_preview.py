from PIL import Image,ImageDraw
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
W=R/'work/finish-NW-final';W.mkdir(exist_ok=True)
choices={1:R/'work/grounding-v2/north/NW/grounding-v3-NW01-a03.png'}
override=R/'work/finish-NW/selection-overrides.json';overrides=json.loads(override.read_text(encoding='utf-8')) if override.exists() else {}
frames=[];rows=[]
for f in range(1,17):
    candidates=sorted((R/'work/grounding-v2/north/NW').glob(f'finish-nw-NW{f:02d}-a[0-9][0-9].png'))
    p=R/overrides[str(f)] if str(f) in overrides else candidates[-1] if candidates else choices.get(f,R/f'frames/run/NW/{f:02d}.png')
    im=Image.open(p).convert('RGBA');frames.append(im);im.save(W/f'{f:02d}.png');rows.append({'frame':f,'source':p.relative_to(R).as_posix()})
canvas=Image.new('RGB',(1600,1720),(39,51,64));d=ImageDraw.Draw(canvas)
for i,im in enumerate(frames):
    x=i%4*400;y=i//4*430;pic=im.resize((400,400),Image.Resampling.LANCZOS);canvas.paste(pic,(x,y),pic);d.text((x+8,y+402),f'NW {i+1:02d} / '+('RIGHT' if i<8 else 'LEFT'),fill='white')
canvas.save(W/'contact.jpg',quality=95)
small=[im.resize((384,384),Image.Resampling.LANCZOS) for im in frames]
for name,ms in [('normal',75),('slow',300)]:small[0].save(W/f'{name}.apng',save_all=True,append_images=small[1:],duration=ms,loop=0,disposal=0,blend=0)
(W/'selection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
base=(R/'work/run-NE-cast/eight-support-review.html').read_text(encoding='utf-8')
base=base.replace('NE','NW').replace('右16→07，左08→15','右01→08，左09→16').replace('eight-support-contact.jpg','contact.jpg').replace("'eight-support-selected-'+String(i+1)","String(i+1)")
(W/'index.html').write_text(base,encoding='utf-8')
print('NW preview built')
