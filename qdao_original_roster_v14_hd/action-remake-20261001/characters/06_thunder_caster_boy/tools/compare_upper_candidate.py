from PIL import Image,ImageDraw
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1]
n=int(sys.argv[1]);stem=sys.argv[2];direction=sys.argv[3] if len(sys.argv)>3 else 'SE';o=Image.open(R/f'runtime/run/{direction}/{n:02}.png').convert('RGBA');c=Image.open(R/'work'/f'{stem}.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
b=Image.new('RGB',(2048,1060),(220,224,222));b.paste(o,(0,0),o);b.paste(c,(1024,0),c);d=ImageDraw.Draw(b);d.text((10,1030),f'current {direction}{n:02}',fill='black');d.text((1034,1030),stem,fill='black');b.save(R/'review'/f'{stem}_compare.jpg',quality=96)
print(R/'review'/f'{stem}_compare.jpg')
