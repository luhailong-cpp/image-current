from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent;src=D/'bench-G3-left-conditioned-v6-bounded-preview-native1254.png';old=Image.open(src).convert('RGBA')
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(old.crop((521,348,749,487)),(521,348));g.paste((255,255,255,0),(585,380,685,455))
p=D/'bench-G3-left-conditioned-v9-right-upper-guide-native1254.png';assert not p.exists();g.save(p)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-G3-left-conditioned-v9-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native neighborhood with hole; v6 provisional explicitly used as base','source':str(src),'sourceSha256':sha(src),'guide':str(p),'guideSha256':sha(p),'holeGuideBox':[585,380,685,455],'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
text=(D/'check_native_rect_generation_v2.py').read_text().replace("(D/'current-native-guide-manifest-v1.json')","Path(job.get('sourceGuideManifest',str(D/'current-native-guide-manifest-v1.json')))")
p=D/'check_native_rect_generation_v4.py';assert not p.exists();p.write_text(text)

