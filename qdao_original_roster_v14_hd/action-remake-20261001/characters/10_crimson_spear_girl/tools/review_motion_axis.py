from pathlib import Path
import av,json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];W=R/'run-axis-revision-20261004';W.mkdir(exist_ok=True)
src=Path(r'C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
c=av.open(str(src));frames=list(c.decode(video=0));frames[0].to_image().save(W/'reference-first-frame.jpg')
for start in [0,2,4,6,8,10,12,14,16]:
    chosen=[f for f in frames if start<=float(f.time)<min(start+1,17.4)][::2]
    out=Image.new('RGB',(6*280,3*365),'#e9e8e1');d=ImageDraw.Draw(out);times=[]
    for i,f in enumerate(chosen):
        im=f.to_image().crop((540,185,740,425)).resize((280,336),Image.Resampling.NEAREST)
        x=i%6*280;y=i//6*365;out.paste(im,(x,y));d.text((x+5,y+340),f'{float(f.time):.3f}s',fill='black');times.append(float(f.time))
    p=W/f'reference-continuous-{start:02}.jpg';out.save(p,quality=94)
    Path(str(p)+'.generation.json').write_text(json.dumps({'operation':'decoded source video consecutive 12fps crop, nearest-neighbor preview, no invented detail','derivedFrom':{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()},'times':times,'crop':[540,185,740,425]},indent=2),encoding='utf-8')
for direction in ['N','S']:
    out=Image.new('RGB',(4*360,4*380),'#e9e8e1');d=ImageDraw.Draw(out)
    for i in range(16):
        p=R/f'runtime/run/{direction}/{i+1:02}.png';im=Image.open(p).crop((330,640,690,1000));x=i%4*360;y=i//4*380;out.paste(im,(x,y),im);d.text((x+6,y+363),f'{direction}{i+1:02}',fill='black')
    out.save(W/f'{direction}-feet-audit.jpg',quality=96)
print(json.dumps({'videoFrames':len(frames),'continuousSheets':9,'currentFeetSheets':2}))
