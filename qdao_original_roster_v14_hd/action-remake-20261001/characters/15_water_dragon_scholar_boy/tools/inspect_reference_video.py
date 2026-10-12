"""Decode the user-provided reference video for close consecutive-frame inspection only."""
from pathlib import Path
import av,json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
VIDEO=Path('C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
out=ROOT/'audit/video-direction-20261004';out.mkdir(parents=True,exist_ok=True)
starts=[0,48,174,330];wanted={n for s in starts for n in range(s,s+24,2)};frames={}
with av.open(str(VIDEO)) as c:
    for n,f in enumerate(c.decode(video=0)):
        if n in wanted:frames[n]=(float(f.time),f.to_image())
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
records=[]
for start in starts:
    sheet=Image.new('RGB',(1440,640),'#dddddd');d=ImageDraw.Draw(sheet)
    refs=[]
    for j,n in enumerate(range(start,start+24,2)):
        t,im=frames[n]; crop=(575,185,715,330)
        tile=im.crop(crop).resize((240,249),Image.Resampling.NEAREST)
        x=j%6*240;y=j//6*320
        d.text((x+6,y+6),f'{t:.3f}s / frame {n}',font=font,fill='black');sheet.paste(tile,(x,y+30))
        refs.append({'decodedFrame':n,'time':t,'crop':crop})
    p=out/f'reference-sequence-{start:03d}.png';sheet.save(p)
    records.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frames':refs})
records[0]['fullFirstFrame']='reference-full-first.png';frames[0][1].save(out/'reference-full-first.png')
(out/'reference-video-inspection.json').write_text(json.dumps({'source':str(VIDEO),'sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'operation':'decode original consecutive frames, crop and nearest-neighbor enlargement for inspection only; not an asset or synthesized detail','sourceRate':'24fps','outputs':records},ensure_ascii=False,indent=2),encoding='utf-8')
print('Decoded 4 consecutive reference strips.')
