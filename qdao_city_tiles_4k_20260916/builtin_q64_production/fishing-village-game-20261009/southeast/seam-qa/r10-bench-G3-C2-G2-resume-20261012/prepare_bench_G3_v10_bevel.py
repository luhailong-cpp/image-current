from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;src=D/'bench-G3-left-conditioned-v9b-bounded-preview-native1254.png';old=Image.open(src).convert('RGBA')
g=Image.new('RGBA',(1254,1254),(255,255,255,0));g.paste(old.crop((521,448,774,597)),(521,448));g.paste((255,255,255,0),(585,480,710,565))
p=D/'bench-G3-left-conditioned-v10-bevel-guide-native1254.png';assert not p.exists();g.save(p)
a=np.asarray(old.convert('RGB')).astype(int);out=[]
for x,e in [(584,500),(710,550)]:
 yy=np.arange(e-10,e+11);scores=a[yy,x,1]+a[yy,x,2]
 out.append({'x':x,'bevelBrightestY':int(yy[scores.argmax()])})
# consolidate all provisional source records without mutating canonical
a=json.loads((D/'bench-G3-left-conditioned-v6.adoption-check.json').read_text());b=json.loads((D/'bench-G3-left-conditioned-v9b.adoption-check.json').read_text());rs={(r['tile'],r['patch']):r for r in a['patches']};rs.update({(r['tile'],r['patch']):r for r in b['patches']})
p=D/'bench-G3-left-conditioned-v9b.composite-base-manifest.json';assert not p.exists();p.write_text(json.dumps({'schemaVersion':1,'patches':list(rs.values()),'canonicalSelectionsModified':False},indent=2))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-G3-left-conditioned-v10-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native bevel neighborhood and hole composition','source':str(src),'sourceSha256':sha(src),'guide':str(D/'bench-G3-left-conditioned-v10-bevel-guide-native1254.png'),'guideSha256':sha(D/'bench-G3-left-conditioned-v10-bevel-guide-native1254.png'),'holeGuideBox':[585,480,710,565],'endpointEvidence':out,'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
print(json.dumps(out))

