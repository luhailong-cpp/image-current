from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw,ImageOps
import numpy as np,json,hashlib
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent;R=Q.parents[1]
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def fill(a):
 im=ImageOps.expand(Image.fromarray(a.astype(np.uint8)*255),border=1,fill=0);ImageDraw.floodfill(im,(0,0),128);return np.asarray(im)[1:-1,1:-1]!=128
p=json.loads((Q/'proposal-v04.json').read_text());g=arr(p['jobs'][2]['source']);trace=json.loads((Q/'g-gold-contour-v04.json').read_text())['bottomInclusive'];cap=np.zeros((1254,1254),bool)
for x,y in zip(range(77,1254),trace):cap[:min(1254,y+1+(35 if x>=565 else 0)),x]=True
a=g.astype(np.int16);warm=(a[:,:,0]>a[:,:,2]-5)&(a[:,:,0]>a[:,:,1]-5)&(a[:,:,0]>60)
bw=Image.fromarray((warm&cap).astype(np.uint8)*255).copy();ImageDraw.floodfill(bw,(300,950),128);mask=fill(np.asarray(bw)==128);mask=np.asarray(Image.fromarray(mask.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5)))>0
assert mask.sum()>547742
mp=Q/'g-complete-gold-object-mask-v05.png';Image.fromarray(mask.astype(np.uint8)*255).save(mp);p['jobs'][2].update({'mask':str(mp),'maskSha256':sha(mp),'selectedPixels':int(mask.sum())})
# New trial is replayed from bases and masks, source RGB copied unchanged.
outs=[];maps=[]
for i,o in enumerate(p['outputs']):
 out=arr(o['base']).copy();ids=np.zeros((4096,4096),np.uint8);tx=[-4096,0][i]
 for j in p['jobs']:
  src=arr(j['source']);m=np.asarray(Image.open(j['mask']))>0;ox,oy=j['originRelativeR09c12'];gx=np.arange(1254)+ox;valid=(gx>=tx)&(gx<tx+4096);si=np.where(valid)[0]
  if not len(si):continue
  dx=gx[si]-tx;mm=m[:,si];reg=out[oy:oy+1254,dx].copy();reg[mm]=src[:,si][mm];out[oy:oy+1254,dx]=reg;reg=ids[oy:oy+1254,dx].copy();reg[mm]=j['id'];ids[oy:oy+1254,dx]=reg
 f=Q/Path(o['file']).name.replace('v04','v05');Image.fromarray(out).save(f);mid=Q/Path(o['sourceID']).name.replace('v04','v05');Image.fromarray(ids).save(mid);o.update({'file':str(f),'sha256':sha(f),'sourceID':str(mid),'sourceIDSha256':sha(mid)})
 replay=arr(o['base']).copy()
 for j in p['jobs']:
  src=arr(j['source']);ox,oy=j['originRelativeR09c12'];gx=np.arange(1254)+ox;valid=(gx>=tx)&(gx<tx+4096);si=np.where(valid)[0]
  if not len(si):continue
  dx=gx[si]-tx;mm=ids[oy:oy+1254,dx]==j['id'];reg=replay[oy:oy+1254,dx].copy();reg[mm]=src[:,si][mm];replay[oy:oy+1254,dx]=reg
 assert np.array_equal(replay,out) and np.array_equal(out[ids==0],arr(o['base'])[ids==0])
 outs.append(out);maps.append(ids)
p['createdAt']=datetime.now(timezone.utc).isoformat();p['maskRevisionNote']='v05 includes full G warm silhouette below the lower-right outline; v04 wrongly followed an internal dark brush mark near G local x695. Only binary source ownership changed.'
p['status']='trial_pending_final_visual_review';p['evidence']=[]
right=Image.fromarray(outs[1]);left=Image.fromarray(outs[0])
for name,box in [('ef',(540,1080,850,1800)),('fd',(1560,1120,1910,1880)),('roofwood-left',(0,1300,1024,1950)),('roofwood-scroll',(750,1350,1850,2100)),('bottom',(742,1800,1766,2180)),('top',(627,614,2004,870)),('g-lower',(1370,1740,1580,1900)),('g-right',(1880,742,2132,1660)),('g-top',(1700,614,2132,870))]:
 f=Q/f'full-object-{name}-v05.png';right.crop(box).save(f);p['evidence'].append({'file':str(f),'sha256':sha(f),'r09c12Crop':box})
f=Q/'full-object-e-left-v05.png';left.crop((3686,742,3942,1390)).save(f);p['evidence'].append({'file':str(f),'sha256':sha(f),'r09c11Crop':[3686,742,3942,1390]})
right.resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'full-object-preview-v05.png')
wr(Q/'proposal-v05.json',p)
print(json.dumps({'outputs':p['outputs'],'gPixels':int(mask.sum())},indent=2))

