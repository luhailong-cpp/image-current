from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
O=R/'work/full-limb-root-20261005'
for a,d,count in [('attack','E',12),('attack','W',12),('run','E',16),('run','SE',16)]:
 for start in range(1,count+1,4):
  board=Image.new('RGB',(1536,644),'#f4efdf');draw=ImageDraw.Draw(board)
  for i,n in enumerate(range(start,min(start+4,count+1))):
   im=Image.open(R/f'frames/{a}/{d}/{n:02}.png').convert('RGBA')
   crop=im.crop((0,630,1024,1024)).resize((768,296),Image.Resampling.LANCZOS)
   x=(i%2)*768;y=(i//2)*322;board.paste(crop,(x,y),crop);draw.text((x+15,y+300),f'{a}/{d}/{n:02}',fill='#23443c')
  board.save(O/f'{a}-{d}-{start:02}-legs.jpg',quality=95)
for p in ['tools/run-grounding-template.html','previews/run-grounding.html']:
 f=R/p;s=f.read_text(encoding='utf-8');s=s.replace('视频反馈后的八方向膝踝鞋轴修订已完成离线复核；客户端未接入。','2026-10-05 全动作手脚复核进行中，北向支撑脚轴正在修正；客户端未接入。').replace('视频脚轴修订已完成','全动作手脚复核进行中');f.write_text(s,encoding='utf-8')
p=R/'STATUS.md';s=p.read_text(encoding='utf-8');s=s.replace('# 02 火符少年当前进度','# 02 火符少年当前进度\n\n2026-10-05：196张全动作手脚复核进行中。按髋—膝—踝—鞋头运动轴检查支撑脚，北向已定位6张外撇问题帧，正在局部重画。以下2026-10-04为上一轮完成记录，不能代替本轮结果。');p.write_text(s,encoding='utf-8')
print('14 aspect-preserving lower-body diagnostic sheets; current status marked in progress')
