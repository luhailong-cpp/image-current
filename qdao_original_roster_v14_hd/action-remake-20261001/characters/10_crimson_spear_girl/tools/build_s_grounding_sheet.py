from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
frames=json.loads((ROOT/'candidate-inventory.json').read_text(encoding='utf-8'))['groups']['run/S']
order=json.loads((ROOT/'run-playback-proposals.json').read_text(encoding='utf-8-sig'))['groups']['run/S']
frames.sort(key=lambda f:order.index(f['frame']))
sheet=Image.new('RGB',(1536,1696),'#eceade');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    native=Image.open(ROOT/f['url'][3:]).convert('RGBA')
    export=Image.new('RGBA',(1024,1024))
    export.alpha_composite(native.resize((860,860),Image.Resampling.LANCZOS),(82,151))
    thumb=export.resize((384,384),Image.Resampling.LANCZOS)
    x=i%4*384;y=i//4*424
    sheet.paste(thumb,(x,y),thumb)
    gy=y+round(942*384/1024)
    draw.line((x,gy,x+384,gy),fill='#769688',width=1)
    draw.text((x+8,y+390),f"play {i+1:02} / S{f['frame']:02} (candidate)",fill='#203c34')
out=ROOT/'preview/run-S-grounding-contact.jpg';sheet.save(out,quality=96)
Path(str(out)+'.generation.json').write_text(json.dumps({'operation':'diagnostic-only whole canvas scaled montage with virtual ground line, not new source pose','file':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'derivedFrom':[{'file':f['url'][3:],'sha256':f['sha256']} for f in frames]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(out))
