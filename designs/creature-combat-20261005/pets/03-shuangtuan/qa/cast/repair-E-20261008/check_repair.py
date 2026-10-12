from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib
BASE=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
QA=BASE/'qa/cast/repair-E-20261008'
sheet=Image.new('RGB',(2048,2176),(45,54,56))
draw=ImageDraw.Draw(sheet)
rows=[]
for n in range(1,17):
    p=BASE/f'runtime/cast/E/{n:02d}.png';im=Image.open(p)
    a=im.getchannel('A');sha=hashlib.sha256(p.read_bytes()).hexdigest()
    rec=json.loads((BASE/f'records/cast/E/{n:02d}.generation.json').read_text(encoding='utf-8-sig'))
    assert im.size==(1024,1024) and im.mode=='RGBA' and a.getextrema()==(0,255)
    assert rec['sha256']==sha
    x=((n-1)%4)*512;y=((n-1)//4)*544
    small=im.resize((512,512),Image.Resampling.LANCZOS)
    sheet.paste(small,(x,y+32),small)
    draw.text((x+8,y+8),f'CAST E {n:02d} | 45ms | '+('repaired' if 4<=n<=14 else 'original'),fill='white')
    rows.append({'frame':n,'file':p.relative_to(BASE).as_posix(),'sha256':sha,'alphaBBox':a.getbbox(),'alphaExtrema':a.getextrema(),'width':im.width,'height':im.height,'pixelsOnRightEdge':sum(v>127 for v in list(a.crop((1023,0,1024,1024)).getdata()))})
assert len(set(r['sha256'] for r in rows))==16
sheet.save(QA/'E-contact-repaired.png')
(QA/'technical.json').write_text(json.dumps({'status':'pass dimensions-alpha-count-distinct-SHA','frames':rows},indent=2),encoding='utf-8')
print(json.dumps({'checked':len(rows),'updated':11,'contact':str(QA/'E-contact-repaired.png'),'rightEdges':[(r['frame'],r['pixelsOnRightEdge']) for r in rows]}))
