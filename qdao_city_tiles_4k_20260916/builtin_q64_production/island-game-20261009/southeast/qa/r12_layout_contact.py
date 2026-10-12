from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1200,860),'#dddddd');draw=ImageDraw.Draw(im)
for i,pid in enumerate(['24','33','34','42','43','44']):
 x=(i%3)*400;y=(i//3)*430
 g=Image.open(root/'guides'/f'r12_c12_p{pid}.layout-only.png').convert('RGB');im.paste(g.resize((400,400)),(x,y+30));draw.text((x+12,y+8),f'p{pid} LAYOUT ONLY',(0,0,0))
im.save(root/'qa/r12_c12-missing-layout-contact.png')
