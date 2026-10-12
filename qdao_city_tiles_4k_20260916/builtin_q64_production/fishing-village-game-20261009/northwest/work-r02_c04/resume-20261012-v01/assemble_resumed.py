from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib
from datetime import datetime, timezone

B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest')
W=B/'work-r02_c04'; D=W/'resume-20261012-v01'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j): Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
def sidpath(m): return m['sourceIdMap']['file'] if isinstance(m['sourceIdMap'],dict) else m['sourceIdMap']
def path(cost, step=3):
    h,w=cost.shape; prev=cost[:,0].copy(); back=np.zeros((h,w),np.int16)
    for x in range(1,w):
        v=np.stack([np.roll(prev,k) for k in range(-step,step+1)])
        for k in range(-step,step+1):
            if k<0:v[k+step,k:]=1e15
            elif k>0:v[k+step,:k]=1e15
        z=np.argmin(v,axis=0);back[:,x]=z-step;prev=v[z,np.arange(h)]+cost[:,x]
    y=int(np.argmin(prev)); line=np.empty(w,int)
    for x in range(w-1,-1,-1):line[x]=y;y-=int(back[y,x])
    return line
def region(src,old,bands):
    # Binary optimal seams select original native pixels, with no blending.
    cost=np.mean(np.abs(src.astype(float)-old.astype(float)),axis=2)+.05
    yy,xx=np.indices(cost.shape); t,b,l,r=bands
    def horizontal(band):
        z=cost.copy();z[(yy<band[0])|(yy>band[1])]=1e12;return path(z)
    def vertical(band):
        z=cost.copy();z[(xx<band[0])|(xx>band[1])]=1e12;return path(z.T)
    top=horizontal(t); bottom=horizontal(b);left=vertical(l);right=vertical(r)
    return (yy>=top[None,:])&(yy<=bottom[None,:])&(xx>=left[:,None])&(xx<=right[:,None])
def proof(rgb,ids,sources,origin,out):
    rows=[];total=0
    assert int((ids==0).sum())==0
    for s in sources:
        yy,xx=np.nonzero(ids==s['sourceId'])
        if not len(xx):continue
        p=Path(s['file']);a=np.asarray(Image.open(p).convert('RGB'));x=xx+origin[0]-s['globalNativeBox'][0];y=yy+origin[1]-s['globalNativeBox'][1]
        valid=(x>=0)&(x<a.shape[1])&(y>=0)&(y<a.shape[0]);bad=int((~valid).sum());mis=int(np.any(rgb[yy[valid],xx[valid]]!=a[y[valid],x[valid]],axis=1).sum());total+=mis
        actual=sha(p);assert actual==s['sha256'];assert bad==0;assert mis==0
        rows.append({'sourceId':s['sourceId'],'file':str(p),'sha256':actual,'pixels':len(xx),'invalidCoordinates':bad,'mismatches':mis})
    p={'pixels':int(ids.size),'uncovered':int((ids==0).sum()),'mismatches':total,'invalidCoordinates':sum(r['invalidCoordinates'] for r in rows),'nativeScaleResampled':False,'feathered':False,'painted':False,'sources':rows};write(out,p);return p

m=read(W/'joint-v2/joint.assembly.json');rgb=np.asarray(Image.open(m['file']).convert('RGB')).copy();ids=np.asarray(Image.open(sidpath(m))).copy();sources=m['sources'];ox,oy=m['globalBox'][:2];patches=[]
for n,bands in [
 ('r02_c04_south_paving_joint_west_20261012_v02',[(220,320),(720,970),(250,390),(840,1010)]),
 ('r02_c04_south_paving_joint_east_20261012_v02',[(270,340),(660,800),(110,220),(650,780)])]:
    p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');src=np.asarray(Image.open(p).convert('RGB'));b=g['globalNativeBox'];x=b[0]-ox;y=b[1]-oy;old=rgb[y:y+1254,x:x+1254];mask=region(src,old,bands);k=max(s['sourceId'] for s in sources)+1
    old[mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=k;mp=D/(n+'.hard-mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp)
    sources.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None,'nativeScaleResampled':False})
    patches.append({'id':n,'sourceId':k,'globalNativeBox':b,'hardMask':str(mp),'hardMaskSHA256':sha(mp),'pixels':int(mask.sum()),'composition':'exact native pixels selected by binary optimal seams; no blending'})
    Image.fromarray(old).save(D/'qa'/(n+'.composed.100pct.png'))

Image.fromarray(rgb).save(D/'joint.context.png');Image.fromarray(ids).save(D/'joint.source-id.png')
jm={'schemaVersion':1,'globalBox':m['globalBox'],'file':str(D/'joint.context.png'),'sha256':sha(D/'joint.context.png'),'sourceIdMap':str(D/'joint.source-id.png'),'sourceIdSHA256':sha(D/'joint.source-id.png'),'sources':sources,'baseAssembly':str(W/'joint-v2/joint.assembly.json'),'baseAssemblySHA256':sha(W/'joint-v2/joint.assembly.json'),'baseImageSHA256':sha(m['file']),'patches':patches,'resampled':False,'feathered':False,'painted':False,'formalAccepted':False,'status':'new-resumed-joint-candidate'};write(D/'joint.assembly.json',jm)
crop=rgb[115:4211,115:4211];ci=ids[115:4211,115:4211];Image.fromarray(crop).save(D/'r02_c04.candidate.png');Image.fromarray(ci).save(D/'r02_c04.source-id.png')
pr=proof(crop,ci,sources,[12288,4096],D/'r02_c04.source-proof.json')
assembly={'schemaVersion':1,'tile':'r02_c04','createdAt':datetime.now(timezone.utc).isoformat(),'candidate':{'file':str(D/'r02_c04.candidate.png'),'sha256':sha(D/'r02_c04.candidate.png')},'sourceIdMap':{'file':str(D/'r02_c04.source-id.png'),'sha256':sha(D/'r02_c04.source-id.png')},'globalCoreBox':[12288,4096,16384,8192],'outputSize':[4096,4096],'sources':sources,'inputs':[{'assembly':str(D/'joint.assembly.json'),'sha256':sha(D/'joint.assembly.json'),'crop':[115,115,4211,4211]}],'overlays':patches,'proof':{'file':str(D/'r02_c04.source-proof.json'),'sha256':sha(D/'r02_c04.source-proof.json'),'pixels':pr['pixels'],'mismatches':pr['mismatches']},'resampled':False,'feathered':False,'painted':False,'actualModel':None,'actualQuality':None,'formalAccepted':False,'status':'complete-candidate-local-QA-pending'};write(D/'r02_c04.assembly.json',assembly)
Image.fromarray(crop).resize((1024,1024),Image.Resampling.LANCZOS).save(D/'qa/r02_c04.new.preview-only.png')

# Independent neighbor delta: only pixels originating in this worker's native art.
ap=B/'delivery-2x2/stage-v4/r03_c04.assembly.json';am=read(ap);basep=B/'delivery-2x2/stage-v4/r03_c04.png';base=np.asarray(Image.open(basep).convert('RGB'));bi=np.asarray(Image.open(sidpath(am)));nimg=base.copy();nids=bi.copy();nsources=am['sources'].copy();band=rgb[4211:,115:4211];bid=ids[4211:,115:4211];h=band.shape[0]
owned=[s for s in sources if str(W/'native').lower() in str(s['file']).lower()]
ownedids=[s['sourceId'] for s in owned];dm=np.isin(bid,ownedids)&np.any(band!=base[:h],axis=2);ds=np.zeros_like(bid,np.uint16)
nextid=max(s['sourceId'] for s in nsources)+1
for s in owned:
    mask=dm&(bid==s['sourceId'])
    if not mask.any():continue
    z=dict(s);z['sourceId']=nextid;z['previousSourceIdInJoint']=s['sourceId'];nsources.append(z);ds[mask]=nextid;nids[:h][mask]=nextid;nextid+=1
nimg[:h][dm]=band[dm]
delta=D/'r03_c04-independent-north-delta';delta.mkdir(exist_ok=True)
ys,xs=np.nonzero(dm);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];x0,y0,x1,y1=bbox
Image.fromarray(band[y0:y1,x0:x1]).save(delta/'r03_c04.delta.rgb.png');Image.fromarray(dm[y0:y1,x0:x1].astype(np.uint8)*255).save(delta/'r03_c04.delta.mask.png');Image.fromarray(ds[y0:y1,x0:x1]).save(delta/'r03_c04.delta.source-id.png')
Image.fromarray(nimg).save(delta/'r03_c04.with-delta.candidate.png');Image.fromarray(nids).save(delta/'r03_c04.with-delta.source-id.png')
dpr=proof(nimg,nids,nsources,[12288,8192],delta/'r03_c04.source-proof.json');assert np.array_equal(nimg[h:],base[h:]);assert int(np.any(nimg[:h][~dm]!=base[:h][~dm],axis=1).sum())==0
da={'schemaVersion':1,'tile':'r03_c04','candidate':{'file':str(delta/'r03_c04.with-delta.candidate.png'),'sha256':sha(delta/'r03_c04.with-delta.candidate.png')},'sourceIdMap':{'file':str(delta/'r03_c04.with-delta.source-id.png'),'sha256':sha(delta/'r03_c04.with-delta.source-id.png')},'globalCoreBox':[12288,8192,16384,12288],'outputSize':[4096,4096],'sources':nsources,'inputs':[{'assembly':str(ap),'sha256':sha(ap),'candidate':str(basep),'candidateSHA256':sha(basep)}],'proof':{'file':str(delta/'r03_c04.source-proof.json'),'sha256':sha(delta/'r03_c04.source-proof.json'),'pixels':dpr['pixels'],'mismatches':0},'resampled':False,'feathered':False,'painted':False,'formalAccepted':False,'status':'independent-neighbor-delta-review-candidate'};write(delta/'r03_c04.with-delta.assembly.json',da)
descriptor={'schemaVersion':1,'ownerTile':'r02_c04','neighborTile':'r03_c04','baseCandidate':str(basep),'baseCandidateSHA256':sha(basep),'baseAssembly':str(ap),'baseAssemblySHA256':sha(ap),'tileCropBox':bbox,'globalBox':[12288+x0,8192+y0,12288+x1,8192+y1],'changedPixels':int(dm.sum()),'rgb':{'file':str(delta/'r03_c04.delta.rgb.png'),'sha256':sha(delta/'r03_c04.delta.rgb.png')},'hardMask':{'file':str(delta/'r03_c04.delta.mask.png'),'sha256':sha(delta/'r03_c04.delta.mask.png'),'values':[0,255]},'sourceIdMap':{'file':str(delta/'r03_c04.delta.source-id.png'),'sha256':sha(delta/'r03_c04.delta.source-id.png')},'candidateAssembly':str(delta/'r03_c04.with-delta.assembly.json'),'outsideMaskChangedPixels':0,'southRowsBeyond1140ChangedPixels':0,'sourceRestriction':'only native images from work-r02_c04/native; current accepted neighbor retained elsewhere','resampled':False,'feathered':False,'painted':False,'formalAccepted':False,'status':'standalone-delta-not-applied-to-root-or-adopted-neighbor'};write(delta/'delta.json',descriptor)
south=np.concatenate([crop[-512:],nimg[:742]],axis=0)
for c in range(4):Image.fromarray(south[:,c*1024:(c+1)*1024]).save(D/'qa'/f'south-final-{c+1}.100pct.png')
for side,im in [('north',rgb[:627,115:4211]),('east',rgb[115:4211,3699:]),('west',rgb[115:4211,:627])]:
    if side=='north':
        for c in range(4):Image.fromarray(im[:,c*1024:(c+1)*1024]).save(D/'qa'/f'{side}-{c+1}.100pct.png')
    else:
        for r in range(4):Image.fromarray(im[r*1024:(r+1)*1024]).save(D/'qa'/f'{side}-{r+1}.100pct.png')
print(json.dumps({'candidate':assembly['candidate'],'proof':{k:pr[k] for k in ['pixels','mismatches','uncovered']},'delta':{'bbox':bbox,'changedPixels':descriptor['changedPixels'],'baseSHA256':descriptor['baseCandidateSHA256'],'outsideMaskChangedPixels':0},'patches':patches},ensure_ascii=False))
