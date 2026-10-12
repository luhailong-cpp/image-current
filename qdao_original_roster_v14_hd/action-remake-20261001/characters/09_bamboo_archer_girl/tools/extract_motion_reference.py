from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import av,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
src=Path('C:/Users/luyua/Documents/xwechat_files/wxid_w7yr2bbfbkv512_a127/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/3b4f71e9130837ef5d278accd4f0069f.mp4')
out=ROOT/'audit/video-reference-20261004';out.mkdir(exist_ok=True)
starts=list(range(0,17,2));wanted={s*24+i for s in starts for i in range(16)}
frames={}
with av.open(str(src)) as c:
 stream=c.streams.video[0]
 meta={'size':[stream.width,stream.height],'fps':str(stream.average_rate),'frames':stream.frames}
 for i,f in enumerate(c.decode(video=0)):
  if i in wanted:frames[i]=f.to_image()
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
sheets=[]
for start in starts:
 sheet=Image.new('RGB',(1120,1160),(239,239,235));draw=ImageDraw.Draw(sheet)
 for colnum,i in enumerate(range(start*24,start*24+16)):
  im=frames[i].crop((575,185,715,320)).resize((280,270),Image.Resampling.NEAREST)
  x=colnum%4*280;y=colnum//4*290
  sheet.paste(im,(x,y));draw.text((x+5,y+271),f'frame {i:03d}  {i/24:.3f}s',font=font,fill=(0,0,0))
 p=out/f'continuous-{start:02d}s.png';sheet.save(p);sheets.append({'file':p.relative_to(ROOT).as_posix(),'frames':list(range(start*24,start*24+16)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
record={'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'video':meta,'crop':[575,185,715,320],'scale':2,'resampling':'nearest inspection enlargement; no new detail','purpose':'Motion-axis and successive leg-swing reference only; other-game design/style not reused','limitations':'Small reference sprite, nameplate/cursor/scene occlusion; contact-sheet inspection is not a claim of real-time playback or resolved fine shoe anatomy','sheets':sheets}
(out/'extraction.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sheets':len(sheets),'continuousFramesPerSheet':16,'source':meta}))

