from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
poly=[(300,602),(970,473),(970,765),(300,765)]
source=D/'G3-bottom-conditioned-v1-guide-native1254.png'
mask=Image.new('L',(1254,1254),0);ImageDraw.Draw(mask).polygon(poly,fill=255)
mp=D/'G3-bottom-conditioned-v2-adopt-mask-native1254.png';assert not mp.exists();mask.save(mp)
guide=Image.open(source).convert('RGBA');alpha=guide.getchannel('A');alpha.paste(0,(0,0),mask);guide.putalpha(alpha)
p=D/'G3-bottom-conditioned-v2-natural-cutout-guide-native1254.png';assert not p.exists();guide.save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(source),'sourceSha256':sha(source),
 'guide':str(p),'guideSha256':sha(p),'adoptMask':str(mp),'adoptMaskSha256':sha(mp),'polygonGuide':poly,
 'polygonWorld':[[x+36060,y+46592] for x,y in poly],'boundingGuideBox':[300,473,971,766],
 'boundingWorldBox':[36360,47065,37031,47358],'nativeSize':[1254,1254],
 'maskOnly':'Mechanical exact-pixel guide hole and adoption mask. No drawing of art or synthesized geometry.',
 'sourceAuthority':'Current selected cores from v1 guide provenance. Source image pixels unchanged outside alpha hole.',
 'canonicalModified':False,'imageResampling':False,'paidApiUsed':False}
(D/'G3-bottom-conditioned-v2-guide-provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guide':str(p),'polygonWorld':meta['polygonWorld']}))
