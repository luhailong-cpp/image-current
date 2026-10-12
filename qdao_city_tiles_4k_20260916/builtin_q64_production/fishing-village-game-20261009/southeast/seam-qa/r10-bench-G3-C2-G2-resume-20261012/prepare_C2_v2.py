from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent; src=D/'bench-C2-right-conditioned-v1-guide-native1254.png'; out=D/'bench-C2-right-conditioned-v2-neighborhood-guide-native1254.png'
assert not out.exists()
old=Image.open(src).convert('RGBA'); im=Image.new('RGBA',(1254,1254),(255,255,255,0)); im.paste(old.crop((526,211,714,844)),(526,211)); im.paste((255,255,255,0),(590,275,650,780)); im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-C2-right-conditioned-v2-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native neighborhood and hole composition','source':str(src),'sourceSha256':sha(src),'file':str(out),'sha256':sha(out),'neighborhoodBox':[526,211,714,844],'blankGuideBox':[590,275,650,780],'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')

