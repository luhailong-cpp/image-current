from pathlib import Path
import json,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
d=sys.argv[1]
p=ROOT/'review'/f'run-{d}-selection.json'
j=json.loads(p.read_text(encoding='utf-8'))
def norm(x):
    if isinstance(x,dict):return {k:norm(v) for k,v in x.items()}
    if isinstance(x,list):return [norm(v) for v in x]
    if isinstance(x,str) and ('run\\' in x or '.png' in x):return x.replace('\\','/')
    return x
j=norm(j);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sheet=Image.new('RGB',(4*288,4*324),(219,215,208));draw=ImageDraw.Draw(sheet)
for k,f in enumerate(j['frames']):
    im=Image.open(ROOT/f['path']).convert('RGBA');im.thumbnail((280,280))
    x=(k%4)*288+4;y=(k//4)*324+24;sheet.paste(im,(x,y),im)
    draw.text((x,y-20),f"{d}{f['frame']:02} / {Path(f['sourcePath']).stem}",fill=(15,20,30))
sheet.save(ROOT/'review'/f'run-{d}-contact.png')
print(str(ROOT/'review'/f'run-{d}-contact.png'))

