from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
s=p.parent/'native'/'s02_01.png'
im=Image.open(s).convert('RGB')
d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',26)
d.line((0,710,620,710),fill=(0,210,255),width=6)
d.line((620,740,1253,740),fill=(0,210,255),width=6)
for x,y0,y1 in [(450,633,708),(815,653,738),(1130,667,738)]:
    d.line((x,y0,x,y1),fill=(255,0,160),width=7)
    d.polygon([(x,y1),(x-12,y1-18),(x+12,y1-18)],fill=(255,0,160))
d.rectangle((610,750,1215,796),fill=(255,255,255))
d.text((621,756),'NEW STONE BOTTOM ON CYAN LINE',font=font,fill=(0,80,120))
out=p/'s02_01.fix02.geometry-guide.png';im.save(out)
(out.with_suffix('.png.derivation.json')).write_text(json.dumps({'file':str(out),'role':'layout-only coordinate annotation; NOT game artwork','derivedFrom':{'file':str(s),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()},'operation':'unscaled native image plus explicit coordinate annotation arrows and target baseline','guideTarget':{'leftBaseBottom':710,'balustradeAndStepBottom':740}},indent=2),encoding='utf-8')
