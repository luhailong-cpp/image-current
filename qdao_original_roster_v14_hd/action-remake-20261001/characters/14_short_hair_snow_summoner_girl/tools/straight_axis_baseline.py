"""Capture immutable pre-review hashes and diagnostic crops, without pose edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'audit/straight-axis-baseline.json'
if not out.exists():
    data={'at':datetime.now(timezone.utc).isoformat(),'requirement':'2026-10-05: hip-knee-ankle-toe direction stays in the movement plane; preserve flexion and two distinct poses per support position; correct frames retained; run 16x75ms.', 'frames':{p.relative_to(R).as_posix():sha(p) for a in ['run','hit','attack','cast'] for p in sorted((R/a).glob('*/*.png')) if p.parent.name!='staging'},'priorFinalAudit':json.loads((R/'audit/video-axis-final-review.json').read_text(encoding='utf-8-sig'))}
    assert len(data['frames'])==196
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
st=R/'run/staging';st.mkdir(exist_ok=True)
for start in [1,9]:
    sheet=Image.new('RGB',(1600,800),(225,229,231));d=ImageDraw.Draw(sheet)
    for i,n in enumerate(range(start,start+8)):
        im=Image.open(R/f'run/E/{n:02}.png').convert('RGBA').crop((260,610,820,990))
        im.thumbnail((400,350),Image.Resampling.LANCZOS)
        x=i%4*400;y=i//4*400
        sheet.paste(im,(x+(400-im.width)//2,y+40),im)
        d.text((x+12,y+12),f'E {n:02}',fill='black')
    sheet.save(st/f'straight-axis-E-{start:02}.jpg',quality=96)
print('196 baseline hashes preserved; E diagnostic sheets ready')
