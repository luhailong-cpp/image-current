from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent
src=D/'eastdeck-G2-conditioned-v1-guide-native1254.png'
out=D/'eastdeck-G2-conditioned-v2-clear-hole-guide-native1254.png'
assert not out.exists()
im=Image.open(src).convert('RGBA'); im.paste((255,255,255,0),(440,340,850,1150)); im.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'eastdeck-G2-conditioned-v2-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native hole composition','source':str(src),'sourceSha256':sha(src),'file':str(out),'sha256':sha(out),'blankGuideBox':[440,340,850,1150],'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')

