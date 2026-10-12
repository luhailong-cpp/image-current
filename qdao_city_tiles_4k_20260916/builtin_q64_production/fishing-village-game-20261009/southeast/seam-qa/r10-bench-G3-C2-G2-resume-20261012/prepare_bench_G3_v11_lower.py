from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;src=D/'bench-G3-left-conditioned-v10b-bounded-preview-native1254.png';old=Image.open(src).convert('RGBA');a=np.asarray(old.convert('RGB')).astype(int)
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(old.crop((521,588,774,757)),(521,588));g.paste((255,255,255,0),(585,620,710,725))
p=D/'bench-G3-left-conditioned-v11-lower-edge-guide-native1254.png';assert not p.exists();g.save(p)
out=[]
for x in [584,710]:
 e=round(582+(x-449)*.45);yy=np.arange(e-20,e+21);v=a[yy,x].mean(1);out.append({'x':x,'darkLowerY':int(yy[v.argmin()])})
a=json.loads((D/'bench-G3-left-conditioned-v9b.composite-base-manifest.json').read_text());b=json.loads((D/'bench-G3-left-conditioned-v10b.adoption-check.json').read_text());rs={(r['tile'],r['patch']):r for r in a['patches']};rs.update({(r['tile'],r['patch']):r for r in b['patches']})
p=D/'bench-G3-left-conditioned-v10b.composite-base-manifest.json';assert not p.exists();p.write_text(json.dumps({'schemaVersion':1,'patches':list(rs.values()),'canonicalSelectionsModified':False},indent=2))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-G3-left-conditioned-v11-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native lower-edge neighborhood and hole','source':str(src),'sourceSha256':sha(src),'guide':str(D/'bench-G3-left-conditioned-v11-lower-edge-guide-native1254.png'),'guideSha256':sha(D/'bench-G3-left-conditioned-v11-lower-edge-guide-native1254.png'),'holeGuideBox':[585,620,710,725],'endpointEvidence':out,'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(json.dumps(out))

