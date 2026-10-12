from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;src=D/'bench-C2-right-conditioned-v1-guide-native1254.png';before=Image.open(src).convert('RGB');a=np.asarray(before).astype(int)
m=np.zeros((1254,1254),np.uint8);rows=[]
for x in range(572,895):
 expected=round(382+(x-572)*199/308)
 ys=np.arange(expected-90,expected+6); rgb=a[ys,x]
 front=(rgb[:,0]-rgb[:,1]>40)&(rgb[:,1]-rgb[:,2]>18)
 hits=ys[front];assert len(hits)>0,(x,expected)
 top=int(hits[-1])+3
 bottom=round(745-(x-572)*.505)
 if top<bottom:m[top:bottom,x]=255
 rows.append([x,top,bottom])
mask=Image.fromarray(m,'L');mp=D/'bench-C2-right-conditioned-v4-natural-floor-adopt-mask-native1254.png';mask.save(mp)
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(before.crop((508,280,959,835)).convert('RGBA'),(508,280));g.paste((255,255,255,0),(0,0,1254,1254),mask)
gp=D/'bench-C2-right-conditioned-v4-natural-floor-guide-native1254.png';g.save(gp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-C2-right-conditioned-v4-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native floor object mask selection','source':str(src),'sourceSha256':sha(src),'mask':str(mp),'maskSha256':sha(mp),'guide':str(gp),'guideSha256':sha(gp),'upperBoundarySelection':'last source saturated timber-front pixel near existing lower beam, plus3px below','upperSourceRGBPredicate':'R-G>40 and G-B>18 in local beam range','lowerBoundarySelection':'source rim top assessed at x621 y723, x650 y710, x700 y685, x750 y660, x800 y634, x850 y607, x880 y591; adopt limit sits2..5px above rim contour','maskRows':rows,'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(json.dumps({'maskBox':mask.getbbox(),'sampleRows':[r for r in rows if r[0] in [572,600,621,650,700,750,800,850,880]]}))

