"""Read-only video analysis crops. Never writes game animation images."""
from pathlib import Path
import av, json, hashlib
from PIL import Image, ImageDraw
B=Path(__file__).resolve().parent.parent
source=Path(r'C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
out=B/'review/video-axis-20261004'
out.mkdir(exist_ok=True)
container=av.open(str(source))
frames=list(container.decode(video=0))
records=[]
for start in [12,60,108,156,204,252,300,348,390]:
    indices=list(range(start,min(start+24,len(frames))))
    sheet=Image.new('RGB',(1200,4*224),(245,243,235)); draw=ImageDraw.Draw(sheet)
    for i,idx in enumerate(indices):
        frame=frames[idx].to_image()
        crop=frame.crop((585,198,705,318)).resize((200,200),Image.Resampling.NEAREST)
        x=(i%6)*200; y=(i//6)*224
        sheet.paste(crop,(x,y+24)); draw.text((x+4,y+5),f'frame {idx:03d} / {idx/24:.3f}s',fill=(25,25,25))
    path=out/f'continuous-{start:03d}.jpg'; sheet.save(path,quality=94)
    records.append({'file':str(path.relative_to(B)),'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':indices,'crop':[585,198,705,318],'operation':'Consecutive original video frames, analysis crop only, nearest-neighbor magnification; no inferred detail.'})
(out/'continuous-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sheets':len(records),'originalFrames':len(frames)}))
