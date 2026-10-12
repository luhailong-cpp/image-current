from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent
before=Image.open(D/'bench-G3-left-conditioned-v6-before-guide-native1254.png').convert('RGB')
boxes=[(520,344,615,435),(520,445,615,529),(520,589,615,677),(520,704,615,825)]
m=Image.new('L',(1254,1254),0);dr=ImageDraw.Draw(m);g=Image.new('RGBA',(1254,1254),(255,255,255,0))
for b in boxes:
 nb=(b[0]-64,b[1]-32,b[2]+64,b[3]+32);g.paste(before.crop(nb).convert('RGBA'),nb[:2]);dr.rectangle((b[0],b[1],b[2]-1,b[3]-1),fill=255)
g.paste((255,255,255,0),(0,0,1254,1254),m)
gp=D/'bench-G3-left-conditioned-v7-four-contours-guide-native1254.png';g.save(gp)
mp=D/'bench-G3-left-conditioned-v7-adopt-mask-native1254.png';m.save(mp)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'bench-G3-left-conditioned-v7-guide-provenance.json').write_text(json.dumps({'operation':'mechanical native four contour neighborhoods and hole composition','source':str(D/'bench-G3-left-conditioned-v6-before-guide-native1254.png'),'sourceSha256':sha(D/'bench-G3-left-conditioned-v6-before-guide-native1254.png'),'holeGuideBoxes':boxes,'guide':str(gp),'guideSha256':sha(gp),'mask':str(mp),'maskSha256':sha(mp),'resampling':False,'generatedPixels':False},indent=2),encoding='utf-8')
text=(D/'check_native_mask_generation_v1.py').read_text().replace("(D/'current-native-guide-manifest-v1.json')","Path(job.get('sourceGuideManifest',str(D/'current-native-guide-manifest-v1.json')))")
cp=D/'check_native_mask_generation_v2.py';assert not cp.exists();cp.write_text(text)
print(json.dumps({'maskBox':m.getbbox(),'guide':str(gp)}))

