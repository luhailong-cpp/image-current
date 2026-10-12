from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
T=Path(__file__).resolve().parent;R=T/'repairs-north-20261011';D=T/'review'/'north-v6';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(cost):
    h,w=cost.shape;parents=np.zeros((h,w),np.int16);prev=cost[0].copy()
    for y in range(1,h):
        c=np.stack([np.pad(prev,(1,0),constant_values=1e20)[:w],prev,np.pad(prev,(0,1),constant_values=1e20)[1:]])
        ix=np.argmin(c,0);parents[y]=np.arange(w)+ix-1;prev=cost[y]+np.min(c,0)
    out=np.empty(h,np.int16);out[-1]=np.argmin(prev)
    for y in range(h-1,0,-1):out[y-1]=parents[y,out[y]]
    return out
v5=read(T/'candidate/r14_c13-north-v5-manifest.json');step=v5['steps'][1].copy();meta=read(R/'north-paving-v1.target.json')
a=Image.open(step['source']).convert('RGB');old=Image.open(meta['target']).convert('RGB');b=Image.open(step['native']).convert('RGB');alpha=np.array(Image.open(step['alpha']))
oa=np.asarray(old,dtype=np.float32);ba=np.asarray(b,dtype=np.float32);cost=np.mean((oa-ba)**2,2)*(1+40*((255-np.minimum(oa.mean(2),ba.mean(2)))/255)**3)
top=path(cost[400:425,:].T)+400;yy,xx=np.mgrid[:1254,:1254];top_alpha=np.uint8(np.clip((yy-top[None,:]+2)/4,0,1)*255)
for x in range(790,931):alpha[:,x]=np.minimum(alpha[:,x],top_alpha[:,x])
mp=R/'north-paving-v1-applied-alpha-v6.png';Image.fromarray(alpha).save(mp)
com=Image.composite(b,old,Image.fromarray(alpha));a.paste(com.crop((0,400,1254,1254)),(1550,0))
out=T/'candidate/r14_c13-4k-north-v6.png';a.save(out)
step.update(id='north-paving-v1-north-endpoint-composition-v6',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),alpha=str(mp),alphaSha256=sha(mp),maskRule=step['maskRule']+' Retain trusted original incoming grout in native x790..930 via minimum-error top cut within y400..424; all immutable northern pixels remain locked.',output=str(out),outputSha256=sha(out))
base=v5['baseAssemblyPointerSnapshot'];ctx=Image.open(base['context']['path']).convert('RGB');ctx.paste(a,(115,115));cp=T/'candidate/r14_c13-context-4326-north-v6.png';ctx.save(cp)
v6=dict(v5);v6.update(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),steps=[v5['steps'][0],step],candidate={'path':str(out),'sha256':sha(out),'size':[4096,4096]},context={'path':str(cp),'sha256':sha(cp),'size':[4326,4326]},exactPixelReplayVerified=False)
(T/'candidate/r14_c13-north-v6-manifest.json').write_text(json.dumps(v6,indent=2),encoding='utf-8')
joined=old.copy();joined.paste(a.crop((1550,0,2804,854)),(0,400));joined.save(D/'paving-joined-100pct.png');joined.crop((350,290,1050,540)).save(D/'paving-boundary-detail-100pct.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out)}))
