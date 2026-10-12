from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageSequence
import json,hashlib
from render_review_board import load_run_timing,gif_durations
B=Path(__file__).resolve().parents[1]
m=json.loads((B/'manifest.json').read_text(encoding='utf-8'));t=load_run_timing()
p=next(p for p in t['profiles'] if p['id']==t['defaultProfile'])
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
dirs=['N','NE','E','SE','S','SW','W','NW']
frames=[];refs=[]
for n in range(1,17):
    im=Image.new('RGB',(960,590),'#e5e9e9');d=ImageDraw.Draw(im)
    d.text((14,9),'15 水龙书生 · 八方向跑步 · 960ms / 圈',font=font,fill='#153d4a')
    for j,direction in enumerate(dirs):
        row=next(r for r in m['frames'] if r['action']=='run' and r['direction']==direction and r['frame']==n)
        refs.append({'slot':row['slot'],'file':row['output'],'sha256':row['sha256']})
        x=j%4*240;y=39+j//4*272
        d.text((x+8,y),direction+' · '+str(n).zfill(2),font=font,fill='#153d4a')
        with Image.open(B/row['output']) as f:
            f=f.resize((240,240),Image.Resampling.LANCZOS);im.paste(f,(x,y+23),f)
    frames.append(im)
dur=gif_durations(p['frameDurationsMs'])
out=B/'preview/run-all-directions.gif'
frames[0].save(out,save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=2,optimize=False)
with Image.open(out) as f: actual=[x.info['duration'] for x in ImageSequence.Iterator(f)]
assert len(actual)==16 and sum(actual)==960
record={'file':'preview/run-all-directions.gif','operation':'preview only; whole canvas 240px thumbnails; no pose synthesis','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'manifestSha256':hashlib.sha256((B/'manifest.json').read_bytes()).hexdigest(),'sourceFrameDurationsMs':p['frameDurationsMs'],'gifActualFrameDurationsMs':actual,'cycleMs':960,'derivedFrom':refs}
(B/'preview/run-all-directions.gif.provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('preview/run-all-directions.gif')
