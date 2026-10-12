"""Blend AI-painted material locally; retain original grout/geometry pixels.
No image blur, spatial resampling, color correction, or geometry warp.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np,json,hashlib
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rid='m02-lower-v1'
a=Image.open(HERE/'inputs'/f'{rid}.png').convert('RGB')
b=Image.open(HERE/'source'/f'{rid}.png').convert('RGB')
y,x=np.mgrid[0:1254,0:1254]
# Only blue stone slab faces. The old line is x348; retain all original grout.
wx=np.minimum(np.clip(x/270,0,1),np.clip((900-x)/350,0,1))
wy=np.minimum(np.clip((y-469)/18,0,1),np.clip((927-y)/18,0,1))
mask=np.rint(wx*wy*255).astype('uint8')
# Known original blue-stone joint lines and their bevels are immutable.
mask[613:632,:]=0
mask[:632,216:234]=0
mask[:,455:479]=0
m=Image.fromarray(mask,'L');p=HERE/'review'/f'{rid}-material-mask.png';m.save(p)
out=a.copy();out.paste(b,(0,0),m);out.save(HERE/'review'/f'{rid}-material-proposal.png')
outside=Image.composite(a,out,m.point(lambda t:255 if t else 0))
assert ImageChops.difference(outside,a).getbbox() is None
rec={'id':rid,'source':str(HERE/'source'/f'{rid}.png'),'sourceSha256':sha(HERE/'source'/f'{rid}.png'),'mask':str(p),'maskSha256':sha(p),'pasteOrigin':[1700,2842],'maskNonzeroBox':list(m.getbbox()),'method':'AI painted blue stone material with scalar edge weights, original grout excluded','noImageBlur':True,'noSourceResampling':True,'noGeometryWarp':True,'originalGroutPreserved':True,'outsideMaskPixelIdentical':True,'candidateChanged':False}
(HERE/'records'/f'{rid}.material-proposal.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rec))
