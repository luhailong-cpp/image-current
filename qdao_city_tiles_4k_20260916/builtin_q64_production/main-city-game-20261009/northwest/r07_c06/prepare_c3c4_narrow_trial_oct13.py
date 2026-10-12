from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
T=Path(__file__).resolve().parent;D=T/'qa/restart-saved-integration-20261013';S=T/'repair-batches/c3c4-upper-gap-02'
reg=json.loads((T/'candidate/native-overlays-20261013-v09.json').read_text());im=Image.open(reg['candidate']['file']).convert('RGB');out=im.copy();n=Image.open(S/'native.png').convert('RGB')
poly=[(619,566),(634,572),(632,620),(644,629),(632,639),(620,631),(622,581),(615,576)]
mask=Image.new('L',(1254,1254),0);ImageDraw.Draw(mask).polygon(poly,fill=255)
# Binary selection from a true native source at unchanged world coordinates.
out.paste(n,(2445,0),mask)
for f in ['c3c4-narrow-mask.png','c3c4-narrow-trial-4096.png','c3c4-narrow-context.png','c3c4-narrow-detail.png']:assert not (D/f).exists()
mask.save(D/'c3c4-narrow-mask.png');out.save(D/'c3c4-narrow-trial-4096.png');out.crop((2940,450,3210,750)).save(D/'c3c4-narrow-context.png');out.crop((3015,535,3120,675)).save(D/'c3c4-narrow-detail.png')
def ref(f):return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
pix=np.array(out);base=np.array(im);m=np.array(mask)>0;ys,xs=np.where(m);assert np.array_equal(pix[ys,xs+2445],np.array(n)[ys,xs]);assert np.count_nonzero(np.any(base!=pix,axis=2))<=len(xs)
record={'candidate':ref(D/'c3c4-narrow-trial-4096.png'),'base':reg['candidate'],'source':ref(S/'native.png'),'mask':ref(D/'c3c4-narrow-mask.png'),'maskPolygonNative':poly,'nativeTileOriginXY':[2445,0],'selectedPixels':len(xs),'pureNativePixels':True,'unchangedOutsideMask':True,'qa':[ref(D/'c3c4-narrow-context.png'),ref(D/'c3c4-narrow-detail.png')],'formalAccepted':False}
(D/'c3c4-narrow-trial.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
