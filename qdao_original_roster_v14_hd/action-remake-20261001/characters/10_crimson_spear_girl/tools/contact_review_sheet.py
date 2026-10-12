from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];W=R/'run-contact-revision-20261004';W.mkdir(exist_ok=True)
for direction in ['N','S']:
    out=Image.new('RGB',(1320,1280),'#e9e8e1');draw=ImageDraw.Draw(out);refs=[]
    for i in range(1,17):
        p=R/'runtime/run'/direction/f'{i:02}.png';im=Image.open(p)
        crop=im.crop((335,675,665,975));x=((i-1)%4)*330;y=((i-1)//4)*320
        out.paste(crop,(x,y),crop);draw.line((x,y+267,x+330,y+267),fill='#5e7e68');draw.text((x+10,y+303),f'{direction}/{i:02}',fill='#21362c')
        refs.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    dest=W/f'{direction}-feet-before.jpg';out.save(dest,quality=95)
    Path(str(dest)+'.generation.json').write_text(json.dumps({'operation':'review-only same crop 335,675,665,975 with ground guide y942; no asset modification','derivedFrom':refs},indent=2)+'\n',encoding='utf-8')
