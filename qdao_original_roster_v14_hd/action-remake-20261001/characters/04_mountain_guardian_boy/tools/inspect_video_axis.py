from pathlib import Path
import av, json, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SRC=Path('C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
out=ROOT/'provenance/audit'
c=av.open(str(SRC)); stream=c.streams.video[0]
frames=[]
for f in c.decode(stream):
    frames.append((float(f.time),f.to_image()))
# Consecutive 24 fps windows. Pixel crops are reference inspection only, never sprite editing.
for start in [0,3,6,9,12,15]:
    selected=[(t,im) for t,im in frames if start<=t<start+1.25]
    sheet=Image.new('RGB',(6*240,5*250),'#eee8d8'); d=ImageDraw.Draw(sheet)
    for k,(t,im) in enumerate(selected[:30]):
        crop=im.crop((575,175,720,320)).resize((230,230),Image.Resampling.NEAREST)
        x=(k%6)*240;y=(k//6)*250
        sheet.paste(crop,(x,y+20));d.text((x+4,y+3),f'{t:.3f}s',fill='black')
    sheet.save(out/f'video_axis_continuous_{start:02}.jpg',quality=95)
(out/'video_axis_reference_decode.json').write_text(json.dumps({'source':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'frameCount':len(frames),'fps':str(stream.average_rate),'width':stream.width,'height':stream.height,'windowsSeconds':[0,3,6,9,12,15],'method':'30 consecutive frames per1.25s window, nearest crop for inspection, no inferred fine shoe anatomy'},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(frames))
