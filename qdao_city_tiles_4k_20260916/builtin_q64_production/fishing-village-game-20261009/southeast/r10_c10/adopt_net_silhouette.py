"""Adopt the connected net silhouette, restoring all other original native pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
base=T/'processed/p24-pre-edit-world-anchor.png';edit=T/'processed/p24-net-world-color.png'
poly=[(0,300),(145,230),(330,200),(470,60),(520,0),(718,0),(718,1180),(284,1060),(284,883),(0,812)]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255)
a=Image.open(base).convert('RGB');b=Image.open(edit).convert('RGB');a.paste(b,(0,0),mask)
out=T/'processed/p24-connected-net-edit.png';a.save(out);mp=T/'processed/p24-connected-net-mask.png';mask.save(mp)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert np.array_equal(np.asarray(a)[np.asarray(mask)==0],np.asarray(Image.open(base).convert('RGB'))[np.asarray(mask)==0])
rec={'file':str(out),'sha256':sha(out),'dimensions':[1254,1254],'globalBox':[39821,37773,41075,39027],'operation':'hard native-pixel silhouette adoption of connected net/canopy lower contour; all bench/floor/post pixels outside polygon restored from pre-edit native world anchor','base':{'path':str(base),'sha256':sha(base)},'repair':{'path':str(edit),'sha256':sha(edit)},'polygonNative':poly,'mask':{'path':str(mp),'sha256':sha(mp)},'maskAntialias':False,'imagePixelBlend':False,'resamplingApplied':False,'outsideMaskExactOriginalPixels':True}
out.with_suffix('.png.derivation.json').write_text(json.dumps(rec,indent=2))
print(json.dumps({'file':str(out),'adoptedPixels':int((np.asarray(mask)>0).sum())}))

