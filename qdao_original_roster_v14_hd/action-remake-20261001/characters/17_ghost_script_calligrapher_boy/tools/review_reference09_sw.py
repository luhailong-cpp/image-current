from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl');O=B/'review/reference09-SW';O.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
sheet=Image.new('RGB',(960,1080),(43,49,52));d=ImageDraw.Draw(sheet)
for n in range(1,17):
 x=((n-1)%4)*240;y=((n-1)//4)*270;im=Image.open(R/'runtime/run/SW'/f'{n:02d}.png').convert('RGBA').resize((240,240),Image.Resampling.LANCZOS);d.text((x+8,y+5),f'09 SW {n:02d}',font=font,fill='white');sheet.paste(im,(x,y+28),im)
sheet.save(O/'reference-16-240.png')

