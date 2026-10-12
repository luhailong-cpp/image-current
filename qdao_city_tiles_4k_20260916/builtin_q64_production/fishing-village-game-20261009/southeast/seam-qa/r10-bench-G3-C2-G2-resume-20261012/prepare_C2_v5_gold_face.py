from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;src=D/'bench-C2-right-conditioned-v4-bounded-preview-native1254.png';before=Image.open(src).convert('RGB')
m=np.zeros((1254,1254),np.uint8);rows=[]
for x in range(555,711):
 top=round(754-(x-555)*.505);bottom=top+54
 m[top+4:bottom-4,x]=255;rows.append([x,top+4,bottom-4])
mask=Image.fromarray(m,'L');mp=D/'bench-C2-right-conditioned-v5-gold-face-adopt-mask-native1254.png';mask.save(mp)
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(before.crop((491,630,775,873)).convert('RGBA'),(491,630));g.paste((255,255,255,0),(0,0,1254,1254),mask)
gp=D/'bench-C2-right-conditioned-v5-gold-face-guide-native1254.png';g.save(gp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-C2-right-conditioned-v5-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native gold face interior mask guide composition','source':str(src),'sourceSha256':sha(src),'mask':str(mp),'maskSha256':sha(mp),'guide':str(gp),'guideSha256':sha(gp),'maskRows':rows,'goal':'remove original x621 rectangular shadow on gold rim top face; preserve source rim silhouette and thin bright bevel','resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(mask.getbbox())

