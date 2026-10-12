from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent;src=D/'bench-C2-right-conditioned-v1-guide-native1254.png'
before=Image.open(src).convert('RGB');m=Image.new('L',(1254,1254),0);ImageDraw.Draw(m).polygon([(572,382),(880,581),(572,780)],fill=255)
mp=D/'bench-C2-right-conditioned-v3-floor-adopt-mask-native1254.png';m.save(mp)
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(before.crop((508,318,944,844)).convert('RGBA'),(508,318));g.paste((255,255,255,0),(0,0,1254,1254),m)
gp=D/'bench-C2-right-conditioned-v3-floor-neighborhood-guide-native1254.png';g.save(gp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-C2-right-conditioned-v3-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native floor compartment polygon hole composition','source':str(src),'sourceSha256':sha(src),'mask':str(mp),'maskSha256':sha(mp),'guide':str(gp),'guideSha256':sha(gp),'maskPolygonGuide':[[572,382],[880,581],[572,780]],'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(m.getbbox())

