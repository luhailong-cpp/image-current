from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for f,y in [(5,884),(6,900)]:
 im=Image.new('RGB',(1024,1024),'white');d=ImageDraw.Draw(im)
 d.text((50,35),'LOWER LIMB POSITION GUIDE ONLY — preserve artwork above hips',font=font,fill='black')
 d.text((50,70),'NORTH / walking away: forward contact projects upward',font=font,fill='black')
 d.line([(440,692),(592,692)],fill=(120,120,120),width=3);d.text((600,676),'pelvis reference',font=font,fill=(90,90,90))
 left=[(476,697),(469,768),(484,y-54),(484,y)]
 right=[(557,697),(583,734),(577,775)]
 d.line(left,fill=(40,90,180),width=8)
 d.line(right,fill=(180,90,40),width=8)
 for pt in left[:-1]:d.ellipse((pt[0]-7,pt[1]-7,pt[0]+7,pt[1]+7),fill=(40,90,180))
 for pt in right:d.ellipse((pt[0]-7,pt[1]-7,pt[0]+7,pt[1]+7),fill=(180,90,40))
 d.rounded_rectangle((454,y-57,514,y),radius=8,outline=(40,90,180),width=4)
 d.line((454,y,514,y),fill=(40,90,180),width=7)
 d.ellipse((549,750,609,817),outline=(180,90,40),width=4)
 d.text((130,y-45),'LEFT heel cup flat on ground',font=font,fill=(40,90,180))
 d.text((624,768),'RIGHT sole raised',font=font,fill=(180,90,40))
 d.text((625,800),'knee folds back',font=font,fill=(180,90,40))
 d.text((140,950),'Do not render guide lines, colors, labels or floor in artwork.',font=font,fill='black')
 im.save(ROOT/f'audit/N{f:02d}-lower-pose-guide.png')

