from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
p=D/'G3-bottom-conditioned-v1-guide-native1254.png'
im=Image.open(p).convert('RGBA');box=[250,597,970,725]
alpha=im.getchannel('A');alpha.paste(0,box);im.putalpha(alpha)
out=D/'G3-bottom-conditioned-v1-cutout-guide-native1254.png';assert not out.exists();im.save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(p),'sourceSha256':sha(p),
 'cutoutGuide':str(out),'cutoutGuideSha256':sha(out),'nativeSize':[1254,1254],
 'frameWorld':[36060,46592,37314,47846],'adoptGuideBox':box,'adoptWorldBox':[36310,47189,37030,47317],
 'reason':'Thin wood-only band below final stone riser, spanning actual G3 artificial bottom cut y47219 with true current fixed wood context on all sides.',
 'originalG3GuideY':627,'canonicalC09C10GuideX':804,'geometryResampling':False,'syntheticGeometry':False,
 'composition':'Exact unchanged native source pixels plus alpha-zero rectangular guide hole only.'}
(D/'G3-bottom-conditioned-v1-cutout-provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta))
