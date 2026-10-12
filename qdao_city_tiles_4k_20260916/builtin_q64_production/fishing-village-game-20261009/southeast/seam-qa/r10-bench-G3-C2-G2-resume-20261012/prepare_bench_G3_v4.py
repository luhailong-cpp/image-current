from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
source=D/'bench-G3-left-conditioned-v1-guide-native1254.png'
crop=[386,256,749,924];hole=[450,320,685,860]
original=Image.open(source).convert('RGBA')
guide=Image.new('RGBA',(1254,1254),(255,255,255,0));guide.paste(original.crop(crop),crop[:2]);guide.paste((255,255,255,0),hole)
out=D/'bench-G3-left-conditioned-v4-neighborhood-clear-hole-guide-native1254.png';assert not out.exists();guide.save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(source),'sourceSha256':sha(source),
 'guide':str(out),'guideSha256':sha(out),'nativeCrop':crop,'nativeDestination':crop[:2],'clearHoleGuideBox':hole,
 'nativeCanvasSize':[1254,1254],'imagePixelResize':False,'imagePixelResampling':False,
 'operation':'Exact native crop pasted at original coordinates on blank guide canvas; hole mechanically cleared. No art synthesized.',
 'canonicalModified':False,'paidApiUsed':False}
(D/'bench-G3-left-conditioned-v4-guide-provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
