"""Local AI-painted ceramic material, with scalar coverage; never blur images."""
import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
case=sys.argv[1];rec=read(HERE/'records'/f'{case}.input.json')
srcpath=HERE/'source'/f'{case}.png';src=Image.open(srcpath).convert('RGB');orig=Image.open(rec['context']).convert('RGB')
assert src.size==orig.size==(1254,1254)
a=np.asarray(orig).astype(float);b=np.asarray(src).astype(float)
blue=lambda z:(z[:,:,1]>45)&(z[:,:,2]>45)&(z[:,:,1]>z[:,:,0]*1.2)&(z[:,:,2]>z[:,:,0]*1.25)
# Retain non-blue architecture and the darkest grout/edge pixels from the input.
allowed=blue(a)&blue(b)
yy,xx=np.mgrid[0:1254,0:1254]
x0,y0,x1,y1=rec['editContextBox']
wx=np.clip(np.minimum(xx-x0,x1-1-xx)/70,0,1)
wy=np.clip(np.minimum(yy-y0,y1-1-yy)/24,0,1)
coverage=np.rint(wx*wy*allowed*255).astype('uint8')
mask=Image.fromarray(coverage);result=orig.copy();result.paste(src,(0,0),mask)
outside=ImageChops.difference(result,orig);outside.paste((0,0,0),(0,0),mask.point(lambda v:255 if v else 0));assert outside.getbbox() is None
maskpath=HERE/'review'/f'{case}-material-mask.png';mask.save(maskpath)
proposal=HERE/'review'/f'{case}-material-proposal.png';result.save(proposal)
crop=[max(0,x0-60),0,min(1254,x1+60),1254]
for title,image in [('before',orig),('after',result)]:image.crop(crop).save(HERE/'review'/f'{case}-{title}-100pct.png')
world=rec['contextWorldBox'];ops=[]
for tid,ox,oy in [('r05_c13',49152,16384),('r06_c13',49152,20480)]:
    w=[max(world[0],ox),max(world[1],oy),min(world[2],ox+4096),min(world[3],oy+4096)]
    if w[0]>=w[2] or w[1]>=w[3]:continue
    crop=[w[0]-world[0],w[1]-world[1],w[2]-world[0],w[3]-world[1]]
    ops.append({'tile':tid,'sourceCrop':crop,'maskCrop':crop,'destinationTileXY':[w[0]-ox,w[1]-oy]})
out={'id':case,'source':str(srcpath),'sourceSha256':sha(srcpath),'mask':str(maskpath),'maskSha256':sha(maskpath),'context':rec['context'],'contextSha256':rec['sha256'],'contextWorldBox':world,'method':'AI painted blue ceramic material with scalar edge coverage; original non-blue architecture and dark grooves excluded','noImageBlur':True,'noSourceResampling':True,'noGeometryWarp':True,'outsideMaskPixelIdentical':True,'maskNonzeroBox':mask.getbbox(),'integerTileOperations':ops,'proposal':str(proposal),'proposalSha256':sha(proposal),'candidateChanged':False,'visualStatus':'awaiting-review'}
save(HERE/'records'/f'{case}.material-proposal.json',out);print(json.dumps(out,ensure_ascii=False,indent=2))
