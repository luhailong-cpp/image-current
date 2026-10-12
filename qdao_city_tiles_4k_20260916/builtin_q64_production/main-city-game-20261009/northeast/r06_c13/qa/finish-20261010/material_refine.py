"""Refine painted roof masks to include blue dark grooves; no raster filtering."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
import numpy as np
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for case in ['roof-left-upper-v1','roof-left-lower-v1']:
    rec=json.loads((HERE/'records'/f'{case}.material-proposal.json').read_text(encoding='utf-8'))
    inp=json.loads((HERE/'records'/f'{case}.input.json').read_text(encoding='utf-8'))
    src=Image.open(rec['source']).convert('RGB');orig=Image.open(rec['context']).convert('RGB')
    a=np.asarray(orig).astype(float);b=np.asarray(src).astype(float)
    blue=lambda z:(z[:,:,1]>z[:,:,0]*1.12)&(z[:,:,2]>z[:,:,0]*1.15)
    allowed=blue(a)&blue(b)
    yy,xx=np.mgrid[0:1254,0:1254];x0,y0,x1,y1=inp['editContextBox']
    wx=np.clip(np.minimum(xx-x0,x1-1-xx)/70,0,1);wy=np.clip(np.minimum(yy-y0,y1-1-yy)/24,0,1)
    mask=Image.fromarray(np.rint(wx*wy*allowed*255).astype('uint8'));result=orig.copy();result.paste(src,(0,0),mask)
    diff=ImageChops.difference(result,orig);diff.paste((0,0,0),(0,0),mask.point(lambda v:255 if v else 0));assert diff.getbbox() is None
    maskpath=HERE/'review'/f'{case}-material-mask-v2.png';mask.save(maskpath)
    outpath=HERE/'review'/f'{case}-material-proposal-v2.png';result.save(outpath)
    result.crop([x0-60,0,x1+60,1254]).save(HERE/'review'/f'{case}-after-v2-100pct.png')
    rec.update({'mask':str(maskpath),'maskSha256':sha(maskpath),'proposal':str(outpath),'proposalSha256':sha(outpath),'maskNonzeroBox':mask.getbbox(),'method':'AI painted blue ceramic including its dark blue grout, scalar edge coverage, non-blue architecture preserved','previousProposal':str(HERE/'records'/f'{case}.material-proposal.json'),'visualStatus':'awaiting-review'})
    (HERE/'records'/f'{case}.material-proposal-v2.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(case,mask.getbbox(),sha(outpath))
