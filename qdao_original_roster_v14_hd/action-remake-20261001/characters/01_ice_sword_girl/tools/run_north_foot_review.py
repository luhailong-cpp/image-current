from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
R=Path(__file__).resolve().parents[1]
d=sys.argv[1];j=json.loads((R/'review'/f'run-{d}-selection.json').read_text(encoding='utf-8'))
out=Image.new('RGB',(4*400,4*260),(207,208,206));dr=ImageDraw.Draw(out)
for k,f in enumerate(j['frames']):
    im=Image.open(R/f['sourcePath']).convert('RGBA');w,h=im.size
    im=im.crop((int(w*.29),int(h*.60),int(w*.80),int(h*.99)));im.thumbnail((392,232))
    x=(k%4)*400+4;y=(k//4)*260+24;out.paste(im,(x,y),im);dr.text((x,y-20),f"{d}{f['frame']:02} {Path(f['sourcePath']).stem}",fill=(10,20,30))
out.save(R/'review'/f'run-{d}-foot-contact-review.png')

