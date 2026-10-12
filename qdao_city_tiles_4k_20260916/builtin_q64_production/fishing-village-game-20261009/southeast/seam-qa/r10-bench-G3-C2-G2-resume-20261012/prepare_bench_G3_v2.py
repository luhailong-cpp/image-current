from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;source=D/'bench-G3-left-conditioned-v1-guide-native1254.png'
im=Image.open(source).convert('RGBA');box=[450,320,685,860]
im.paste((255,255,255,0),box)
out=D/'bench-G3-left-conditioned-v2-clear-hole-guide-native1254.png';assert not out.exists();im.save(out)
old=np.asarray(Image.open(source).convert('RGBA'));new=np.asarray(im);mask=np.zeros((1254,1254),bool);mask[320:860,450:685]=True
assert np.array_equal(old[~mask],new[~mask])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(source),'sourceSha256':sha(source),
 'guide':str(out),'guideSha256':sha(out),'holeGuideBox':box,'holeWorldBox':[31000,40520,31235,41060],
 'fixedEndpointSamplesGuide':{'leftX449':{'goldTopY':344,'darkLowerY':582},'rightX685':{'goldTopY':437,'darkLowerY':689}},
 'operation':'Mechanical native guide composition: replace hole with clear RGBA; every art pixel outside hole exact.',
 'imageResampling':False,'syntheticGeometryRepair':False,'canonicalModified':False,'paidApiUsed':False}
(D/'bench-G3-left-conditioned-v2-guide-provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
