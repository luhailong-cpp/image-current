from pathlib import Path
import json, hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
inv=json.loads((ROOT/'candidate-inventory.json').read_text(encoding='utf-8-sig'))
for group in ['hit/E','hit/W','cast/E','cast/W','attack/E','attack/W']:
    fs=inv['groups'].get(group,[])
    sh=Image.new('RGB',(4*384,((len(fs)+3)//4)*420),'#e9e8e1')
    d=ImageDraw.Draw(sh)
    for i,f in enumerate(fs):
        p=ROOT/'candidate'/group/f"{f['frame']:02}.png"
        if not p.exists():continue
        im=Image.open(p);im.thumbnail((384,384));x=i%4*384;y=i//4*420
        sh.paste(im,(x,y),im);d.line((x,y+942*384/1024,x+384,y+942*384/1024),fill='#8a9993')
        d.text((x+8,y+392),f"{group} {f['frame']:02} provisional",fill='#223e33')
    out=ROOT/'preview'/(group.replace('/','-')+'-registered.jpg');sh.save(out,quality=94)
    Path(str(out)+'.generation.json').write_text(json.dumps({'file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'diagnostic full-canvas contact sheet','derivedFrom':[{'file':(Path('candidate')/group/f"{f['frame']:02}.png").as_posix()} for f in fs]},indent=2)+'\n',encoding='utf-8')
print('Battle registered sheets refreshed')

