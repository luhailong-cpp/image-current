"""Read the supplied video and create compact sequential observation boards only."""
from pathlib import Path
import av,json,hashlib
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
source=Path('C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',13)
decoded=[]
with av.open(str(source)) as stream:
 for n,f in enumerate(stream.decode(video=0)):
  decoded.append((n,float(f.time),f.to_image().crop((570,190,715,340))))
records=[]
for start in [0,96,192,288,384]:
 items=decoded[start:min(start+32,len(decoded))]
 board=Image.new('RGB',(8*174,4*200),'#d5d7d8');draw=ImageDraw.Draw(board)
 for k,(n,t,im) in enumerate(items):
  x=(k%8)*174;y=(k//8)*200
  board.paste(im.resize((174,180),Image.Resampling.NEAREST),(x,y));draw.text((x+3,y+182),f'{n:03d}  {t:.3f}s',font=font,fill='#203544')
 p=R/'review'/f'video_reference_sequence_{start:03d}_20261004.jpg';board.save(p,quality=92)
 records.append({'file':p.relative_to(R).as_posix(),'sourceFrames':[n for n,t,im in items],'startSeconds':items[0][1],'endSeconds':items[-1][1],'operation':'contiguous original 24fps frames, fixed ROI x570 y190 145x150; nearest view enlargement only'})
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'decodedFrames':len(decoded),'lastFrameSeconds':decoded[-1][1],'reviewBoards':records,'purpose':'motion plane and continuity reference only; character is small and occluded, shoe detail uncertain; not 06 identity/style input'}
(R/'records/reference_video_observation_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'decoded':len(decoded),'boards':len(records)}))
