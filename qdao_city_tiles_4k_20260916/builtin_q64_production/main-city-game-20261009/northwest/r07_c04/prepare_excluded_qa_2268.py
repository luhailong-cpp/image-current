from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).parent;name='r07_c04-candidate-native-bridges-2268d482e68c2928';m=json.loads((P/'candidate'/name/'assembly.json').read_text());im=Image.open(m['output']['file']);q=P/'qa'/name
out=[]
for n,box,rot in [('paving-excluded-right',[2645,2842,2965,3402],True),('paving-excluded-bottom',[2445,3242,2965,3562],False)]:
 c=im.crop(box)
 if rot:c=c.transpose(Image.Transpose.ROTATE_90)
 f=q/(n+'.png');c.save(f);out.append(dict(name=n,file=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),cropLTRB=box,rotationCCW90=rot,nativePixelScale=1,sourceResampled=False,derivedFrom=m['output']))
(q/'excluded-boundary-crops.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'nativeStored':len(list((P/'native').glob('*.png'))),'selected':len(json.loads((P/'selection.json').read_text())),'bridgeStored':len(list((P/'bridges').glob('*/native.png')))}))

