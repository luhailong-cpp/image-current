from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;src=D/'eastdeck-G2-conditioned-v4-bounded-preview-native1254.png'
before=Image.open(src).convert('RGB');a=np.asarray(before);mask=np.zeros((1254,1254),np.uint8)
wood=(a[:,:,0].astype(int)-a[:,:,2].astype(int))>50
mask[210:340,440:850]=np.where(wood[210:340,440:850],255,0)
m=Image.fromarray(mask,'L');mp=D/'eastdeck-G2-conditioned-v5-top-adopt-mask-native1254.png';m.save(mp)
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(before.crop((376,146,914,404)).convert('RGBA'),(376,146));g.paste((255,255,255,0),(0,0,1254,1254),m)
gp=D/'eastdeck-G2-conditioned-v5-top-neighborhood-guide-native1254.png';g.save(gp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'eastdeck-G2-conditioned-v5-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native floor-only object mask guide composition','source':str(src),'sourceSha256':sha(src),'mask':str(mp),'maskSha256':sha(mp),'guide':str(gp),'guideSha256':sha(gp),'maskRect':[440,210,850,340],'maskSelection':'source R minus B >50 selects existing wood; stone pixels protected','resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(json.dumps({'maskBox':m.getbbox(),'maskPixels':int((mask==255).sum())}))

