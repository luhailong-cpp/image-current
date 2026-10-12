from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
selected={'E':{7:'07-v1',8:'08-v2',15:'15-v1',16:'16-v1'},'W':{13:'13-v2',14:'14-v1',15:'15-v4',16:'16-v4'}}
for d,m in selected.items():
 sheet=Image.new('RGB',(1024,1120),'#c6d4d9');draw=ImageDraw.Draw(sheet)
 for i in range(1,17):
  src=R/(f'drafts/axis-20261004/run/{d}/{m[i]}.png' if i in m else f'candidate/run/{d}/{i:02}.png')
  im=Image.open(src).resize((256,256),Image.Resampling.LANCZOS);x=(i-1)%4*256;y=(i-1)//4*280
  sheet.paste(im,(x,y+24),im);draw.text((x+4,y+4),f'{d}{i:02} '+('NEW' if i in m else ''),fill='black')
 sheet.save(R/f'review/axis-{d}-final-sequence-256-20261004.png')
