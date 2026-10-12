from PIL import Image,ImageDraw
from pathlib import Path
import sys
base=Path(__file__).resolve().parent
action=sys.argv[1]; direction=sys.argv[2]
files=sorted((base/'runtime'/action/direction).glob('*.png'))
size=360; cols=4; rows=(len(files)+cols-1)//cols
out=Image.new('RGB',(cols*size,rows*(size+25)),(64,76,82));draw=ImageDraw.Draw(out)
for k,p in enumerate(files):
 im=Image.open(p).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
 x=(k%cols)*size;y=(k//cols)*(size+25)
 out.paste(im,(x,y),im);draw.text((x+8,y+size+3),f'{action}-{direction}-{p.stem}',fill='white')
folder=base/'qa';folder.mkdir(exist_ok=True)
dest=folder/f'{action}-{direction}-contact.jpg';out.save(dest,quality=95)
print(dest)
