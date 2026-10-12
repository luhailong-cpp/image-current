from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent; src=D/'eastdeck-G2-conditioned-v1-guide-native1254.png'; out=D/'eastdeck-G2-conditioned-v3-neighborhood-guide-native1254.png'
assert not out.exists()
old=Image.open(src).convert('RGBA'); im=Image.new('RGBA',(1254,1254),(255,255,255,0)); im.paste(old.crop((376,276,914,1214)),(376,276)); im.paste((255,255,255,0),(440,340,850,1150)); im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'eastdeck-G2-conditioned-v3-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native neighborhood and hole composition','source':str(src),'sourceSha256':sha(src),'file':str(out),'sha256':sha(out),'neighborhoodBox':[376,276,914,1214],'blankGuideBox':[440,340,850,1150],'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')

