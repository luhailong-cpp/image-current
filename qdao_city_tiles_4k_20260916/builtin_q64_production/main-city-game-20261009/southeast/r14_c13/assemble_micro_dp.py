from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
T=Path(__file__).resolve().parent;R=T/'repairs';D=T/'review'/'micro-dp';D.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(cost):
    h,w=cost.shape; parent=np.zeros((h,w),np.int16); prev=cost[0].copy()
    for y in range(1,h):
        choices=np.stack([np.pad(prev,(1,0),constant_values=1e20)[:w],prev,np.pad(prev,(0,1),constant_values=1e20)[1:]])
        ix=np.argmin(choices,axis=0);parent[y]=np.arange(w)+ix-1;prev=cost[y]+np.min(choices,axis=0)
    out=np.empty(h,np.int16);out[-1]=np.argmin(prev)
    for y in range(h-1,0,-1):out[y-1]=parent[y,out[y]]
    return out
source=T/'candidate/r14_c13-4k-fix-middle-junction.png';a=Image.open(source).convert('RGB');steps=[]
for i in ['fix-small-upper','fix-small-lower']:
    meta=read(R/(i+'.target.json'));rect=meta['cropBoxIn4096'];native=R/(i+'-native.png');b=Image.open(native).convert('RGB');old=a.crop(rect)
    assert np.array_equal(np.asarray(old),np.asarray(Image.open(meta['target']).convert('RGB')))
    oa=np.asarray(old,dtype=np.float32);ba=np.asarray(b,dtype=np.float32)
    cost=np.mean((oa-ba)**2,axis=2)
    darkness=(255-np.minimum(oa.mean(2),ba.mean(2)))/255
    cost*=1+10*darkness**3
    band=200;lo=4
    left=path(cost[:,lo:band])+lo
    right=1253-(path(cost[:,::-1][:,lo:band])+lo)
    top=path(cost.T[:,lo:band])+lo
    bottom=1253-(path(cost[::-1,:].T[:,lo:band])+lo)
    yy,xx=np.mgrid[:1254,:1254]
    dd=np.minimum.reduce([xx-left[:,None],right[:,None]-xx,yy-top[None,:],bottom[None,:]-yy])
    alpha=np.uint8(np.clip((dd+2)/4,0,1)*255);mask=Image.fromarray(alpha)
    maskpath=R/(i+'-dp-alpha.png');mask.save(maskpath)
    a.paste(Image.composite(b,old,mask),(rect[0],rect[1]))
    out=T/'candidate'/('r14_c13-4k-'+i+'-dp.png');a.save(out)
    entry=dict(id=i+'-dp',createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=str(source),sourceSha256=sha(source),native=str(native),nativeSha256=sha(native),placement=rect,alpha=str(maskpath),alphaSha256=sha(maskpath),maskRule='Four minimum-error cuts within outer 4..200 native pixel bands; dark-geometry error weighted; 4px linear alpha; no resizing or blur',output=str(out),outputSha256=sha(out),outsideRepairUnchanged=True,formalAccepted=False)
    steps.append(entry);source=out
    a.crop(rect).save(D/(i+'-composed-100pct.png'))
mf=D/'composition-manifest.json';mf.write_text(json.dumps({'base':str(T/'candidate/r14_c13-4k-fix-middle-junction.png'),'steps':steps,'formalAccepted':False},indent=2),encoding='utf-8')
for k,(x,y) in enumerate([(1570,650),(1570,990),(2503,2040),(2460,2600)]):a.crop((x-240,y-240,x+240,y+240)).save(D/f'micro-{k}-100pct.png')
a.resize((1024,1024),Image.Resampling.LANCZOS).save(D/'overview-preview-only.png')
print(json.dumps({'candidate':str(source),'manifest':str(mf)}))
