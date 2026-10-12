from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
T=Path(__file__).resolve().parent;R=T/'repairs-north-20261011';D=T/'review'/'north-v5';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    assert not Path(p).exists(),p
    Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def path(cost):
    h,w=cost.shape;parent=np.zeros((h,w),np.int16);prev=cost[0].copy()
    for y in range(1,h):
        choices=np.stack([np.pad(prev,(1,0),constant_values=1e20)[:w],prev,np.pad(prev,(0,1),constant_values=1e20)[1:]])
        ix=np.argmin(choices,axis=0);parent[y]=np.arange(w)+ix-1;prev=cost[y]+np.min(choices,axis=0)
    out=np.empty(h,np.int16);out[-1]=np.argmin(prev)
    for y in range(h-1,0,-1):out[y-1]=parent[y,out[y]]
    return out
base=read(T/'candidate/latest-assembly.json');source=Path(base['candidate']['path']);a=Image.open(source).convert('RGB');original=np.asarray(a).copy();steps=[]
for i in ['north-leaves-v1','north-paving-v1']:
    meta=read(R/(i+'.target.json'));x=meta['southCropBox'][0];north=Path(meta['northSource']);assert sha(north)==meta['northSourceSha256']
    old=Image.open(meta['target']).convert('RGB');assert np.array_equal(np.asarray(a.crop(meta['southCropBox'])),np.asarray(old)[400:])
    native=R/(i+'-native.png');b=Image.open(native).convert('RGB');oa=np.asarray(old,dtype=np.float32);ba=np.asarray(b,dtype=np.float32)
    cost=np.mean((oa-ba)**2,axis=2)*(1+10*((255-np.minimum(oa.mean(2),ba.mean(2)))/255)**3)
    left=path(cost[:,4:200])+4 if x else np.full(1254,-5)
    right=1253-(path(cost[:,::-1][:,4:200])+4)
    bottom=path(cost[950:1200,:].T)+950
    yy,xx=np.mgrid[:1254,:1254];dd=np.minimum.reduce([xx-left[:,None],right[:,None]-xx,bottom[None,:]-yy]);alpha=np.uint8(np.clip((dd+2)/4,0,1)*255)
    alpha[:400]=0
    mask=Image.fromarray(alpha);mp=R/(i+'-applied-alpha.png');mask.save(mp)
    a.paste(Image.composite(b,old,mask).crop((0,400,1254,1254)),(x,0))
    out=T/'candidate'/('r14_c13-4k-'+i+'-applied.png');assert not out.exists();a.save(out)
    entry={'id':i,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),'sourceSha256':sha(source),'native':str(native),'nativeSha256':sha(native),'nativeCropBox':[0,400,1254,1254],'tilePlacementBox':meta['southCropBox'],'alpha':str(mp),'alphaSha256':sha(mp),'maskRule':'Northern old tile hard locked; apply generated rows400..1253 only to r14. Side/bottom minimum-error cuts with4px linear alpha; no resizing or blur.','output':str(out),'outputSha256':sha(out),'northSource':str(north),'northSourceSha256':sha(north),'oldNorthUnchanged':True,'formalAccepted':False}
    steps.append(entry);source=out
    joined=Image.open(meta['target']).convert('RGB');joined.paste(a.crop(meta['southCropBox']),(0,400));joined.save(D/(i+'-joined-100pct.png'))
    joined.crop((0,180,1254,700)).save(D/(i+'-north-boundary-100pct.png'))
    joined.crop((0,800,1254,1254)).save(D/(i+'-south-composition-edge-100pct.png'))
outside=np.ones((4096,4096),bool)
for s in steps:
    x,y,x2,y2=s['tilePlacementBox'];outside[y:y2,x:x2]=False
assert np.array_equal(original[outside],np.asarray(a)[outside])
ctx=Image.open(base['context']['path']).convert('RGB');ctx.paste(a,(115,115));cp=T/'candidate/r14_c13-context-4326-north-v5.png';ctx.save(cp)
manifest={'tile':'r14_c13','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseAssemblyPointerSnapshot':base,'steps':steps,'candidate':{'path':str(source),'sha256':sha(source),'size':[4096,4096]},'context':{'path':str(cp),'sha256':sha(cp),'size':[4326,4326]},'outsideRepairUnchanged':True,'resampled':False,'exactPixelReplayVerified':False,'internalArtQA':'pending_north_visual','externalNeighborSeamQA':'pending_full_edges','formalAccepted':False}
mp=T/'candidate/r14_c13-north-v5-manifest.json';write(mp,manifest)
old=Image.open(steps[0]['northSource']).convert('RGB');strip=Image.new('RGB',(4096,800));strip.paste(old.crop((0,3696,4096,4096)),(0,0));strip.paste(a.crop((0,0,4096,400)),(0,400))
for k in range(4):strip.crop((k*1024,0,(k+1)*1024,800)).save(D/f'full-north-quarter{k}-100pct.png')
a.resize((1024,1024),Image.Resampling.LANCZOS).save(D/'overview-preview-only.png')
print(json.dumps({'candidate':str(source),'manifest':str(mp),'context':str(cp)}))
