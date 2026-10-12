"""Adapt approved additive RGB field only; retain all native geometry and pixels.

Image pixels are never resampled, blended or blurred. Gaussian smoothing applies
only to measured RGB offset profiles. All reconstructed art pixels are exact
native v6/v7/v8 generated source pixels plus the saved bounded additive field.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent
STEM='r12c08-wall-rock-rail-color-finish-v1'
RECT=[350,280,950,830];WORLD=[32500,45530,33100,46080];FRAME=[32150,45250,33404,46504]
RING=[[350,280,950,344],[350,766,950,830],[350,344,414,766],[886,344,950,766]]
LOCAL=[[350,400,430,530],[840,280,950,390],[600,280,840,344]]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
guidepath=D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png'
authority=np.asarray(Image.open(guidepath).convert('RGB'),dtype=np.uint8)
rawpaths={v:D/f'r12c08-wall-rock-conditioned-v{v}-raw.png' for v in [6,7,8]}
raws={v:np.asarray(Image.open(p).convert('RGB'),dtype=np.uint8) for v,p in rawpaths.items()}
composed=authority.copy();ids=np.zeros((1254,1254),np.uint8)
for version,boxes in [(6,[RECT]),(7,RING),(8,LOCAL)]:
    for x0,y0,x1,y1 in boxes:
        composed[y0:y1,x0:x1]=raws[version][y0:y1,x0:x1]
        ids[y0:y1,x0:x1]=version
beforepath=D/'r12c08-wall-rock-conditioned-v8-border-bounded-preview.png'
before=np.asarray(Image.open(beforepath).convert('RGB'),dtype=np.uint8)
assert np.array_equal(composed,before),'Exact v6/v7/v8 source replay must pass'
composition_npz=D/(STEM+'-native-source-replay.npz');assert not composition_npz.exists()
np.savez_compressed(composition_npz,sourceVersionIds=ids,rawComposedNative=before,
                    guideFrameWorld=np.array(FRAME),wallRockBoxWorld=np.array(WORLD))

def solve_field(aa,bb):
    h,w=aa.shape[:2]
    def profile(a,b,vertical):
        diff=a-b
        grad=lambda x:np.maximum(np.max(np.abs(np.gradient(x,axis=0)),axis=2),np.max(np.abs(np.gradient(x,axis=1)),axis=2))
        mask=(grad(a)<6)&(grad(b)<6)&(np.max(np.abs(diff),axis=2)<50)
        if not vertical:diff=diff.swapaxes(0,1);mask=mask.T
        n=len(diff);rv=np.zeros((n,3),np.float32);valid=mask.sum(axis=1)>=4
        for i in np.flatnonzero(valid):rv[i]=np.median(diff[i][mask[i]],axis=0)
        kernel=np.exp(-.5*(np.arange(-72,73)/24)**2);kernel/=kernel.sum()
        den=np.convolve(np.pad(valid.astype(float),(72,72),mode='edge'),kernel,mode='valid')
        num=np.stack([np.convolve(np.pad(rv[:,c]*valid,(72,72),mode='edge'),kernel,mode='valid') for c in range(3)],axis=1)
        out=num/np.maximum(den[:,None],1e-8);out[den<.15]=0
        return np.clip(out,-24,24),int(mask.sum())
    curves={};counts={}
    for side,a,b,vert in [('left',aa[:,:24],bb[:,:24],True),('right',aa[:,-24:],bb[:,-24:],True),
                           ('top',aa[:24],bb[:24],False),('bottom',aa[-24:],bb[-24:],False)]:
        curves[side],counts[side]=profile(a,b,vert)
    gx=np.linspace(0,w-1,int(np.ceil((w-1)/16))+1);gy=np.linspace(0,h-1,int(np.ceil((h-1)/16))+1)
    field=np.zeros((len(gy),len(gx),3),np.float32);fixed=np.zeros(field.shape[:2],bool)
    for side,p in curves.items():
        axis=gy if side in ('left','right') else gx
        q=np.stack([np.interp(axis,np.arange(len(p)),p[:,c]) for c in range(3)],axis=1)
        if side=='left':field[:,0]=q;fixed[:,0]=True
        if side=='right':field[:,-1]=q;fixed[:,-1]=True
        if side=='top':field[0]=q;fixed[0]=True
        if side=='bottom':field[-1]=q;fixed[-1]=True
    for iy,ix,v,hp in [(0,0,'left','top'),(0,-1,'right','top'),(-1,0,'left','bottom'),(-1,-1,'right','bottom')]:
        field[iy,ix]=(curves[v][iy]+curves[hp][ix])/2
    yy,xx=np.meshgrid(gy,gx,indexing='ij');fixed|=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])>=256
    iy,ix=np.indices(fixed.shape);masks=[(~fixed)&((iy+ix)%2==p) for p in (0,1)]
    for iteration in range(4000):
        old=field.copy()
        for mask in masks:
            total=np.zeros_like(field);total[1:]+=field[:-1];total[:-1]+=field[1:];total[:,1:]+=field[:,:-1];total[:,:-1]+=field[:,1:]
            field[mask]+=1.8*(total[mask]/4-field[mask])
        if np.max(np.abs(field-old))<.00002:break
    else:raise RuntimeError('Bounded harmonic RGB field did not converge')
    horiz=np.stack([np.stack([np.interp(np.arange(w),gx,row[:,c]) for c in range(3)],axis=1) for row in field])
    full=np.stack([np.stack([np.interp(np.arange(h),gy,horiz[:,x,c]) for c in range(3)],axis=1) for x in range(w)],axis=1).astype(np.float32)
    assert np.abs(full).max()<=24.0001
    return full,field,gx,gy,curves,counts,iteration

x0,y0,x1,y1=RECT
aa=authority[y0:y1,x0:x1].astype(np.float32)
delta=np.zeros((1254,1254,3),np.float32);fields=[]
for v in [6,7,8]:
    bb=raws[v][y0:y1,x0:x1].astype(np.float32)
    full,grid,gx,gy,curves,counts,it=solve_field(aa,bb)
    fp=D/(STEM+f'-v{v}-rgb-field.npz');assert not fp.exists()
    np.savez_compressed(fp,additiveRgb=full,gridRgb=grid,gridX=gx,gridY=gy,
                        left=curves['left'],right=curves['right'],top=curves['top'],bottom=curves['bottom'])
    mask=ids[y0:y1,x0:x1]==v
    delta[y0:y1,x0:x1][mask]=full[mask]
    fields.append({'generatedVersion':v,'generated':str(rawpaths[v]),'generatedSha256':sha(rawpaths[v]),
                   'field':str(fp),'fieldSha256':sha(fp),'maximumFloatCorrection':float(np.abs(full).max()),
                   'validFlatColorSamples':counts,'iterations':it,'actualAppliedPixels':int(mask.sum())})
after=np.uint8(np.clip(np.rint(before.astype(np.float32)+delta),0,255))
actual=np.abs(after.astype(np.int16)-before.astype(np.int16));maxdelta=int(actual.max());assert maxdelta<=24
assert np.array_equal(after[ids==0],before[ids==0])
assert np.array_equal(after[0:241,320:650],before[0:241,320:650])
addnpz=D/(STEM+'-combined-additive-field.npz');assert not addnpz.exists()
np.savez_compressed(addnpz,additiveRgb=delta,sourceVersionIds=ids,sourceNativeBefore=before,
                    expectedNativeAfter=after,wallRockRectGuide=np.array(RECT),wallRockBoxWorld=np.array(WORLD))
replay=np.uint8(np.clip(np.rint(before.astype(np.float32)+np.load(addnpz)['additiveRgb']),0,255))
assert np.array_equal(replay,after)
outguide=D/(STEM+'-provisional-guide-native1254.png');assert not outguide.exists();Image.fromarray(after).save(outguide)

coordinated=json.loads((D/'r12c08-wall-rock-rail-coordinated-v1.patch-manifest.json').read_text(encoding='utf-8'))
patches=[]
for rec in coordinated['patches']:
    im=np.asarray(Image.open(rec['file']).convert('RGB'),dtype=np.uint8).copy();initial=im.copy();nb=rec['nativeFrameWorld']
    inter=[max(nb[0],WORLD[0]),max(nb[1],WORLD[1]),min(nb[2],WORLD[2]),min(nb[3],WORLD[3])]
    nx0,ny0,nx1,ny1=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]]
    gx0,gy0,gx1,gy1=[inter[0]-FRAME[0],inter[1]-FRAME[1],inter[2]-FRAME[0],inter[3]-FRAME[1]]
    # Replay exactly the RGB field on existing candidate pixels; no old pixels used as image fill.
    localdelta=delta[gy0:gy1,gx0:gx1]
    im[ny0:ny1,nx0:nx1]=np.uint8(np.clip(np.rint(im[ny0:ny1,nx0:nx1].astype(np.float32)+localdelta),0,255))
    mask=np.zeros((1254,1254),bool);mask[ny0:ny1,nx0:nx1]=True
    assert np.array_equal(im[~mask],initial[~mask])
    path=D/(STEM+'-'+rec['tile']+'-'+rec['patch']+'-provisional-native1254.png');assert not path.exists();Image.fromarray(im).save(path)
    patches.append({'tile':rec['tile'],'patch':rec['patch'],'file':str(path),'sha256':sha(path),
                    'nativeFrameWorld':nb,'source':rec['file'],'sourceSha256':sha(rec['file']),
                    'worldColorBox':inter,'nativeColorBox':[nx0,ny0,nx1,ny1],
                    'maximumActualChannelDelta':int(np.abs(im.astype(np.int16)-initial.astype(np.int16)).max()),
                    'outsideColorBoxPixelReplayExact':True,'wallRockCoreAdoption':rec['wallRockCoreAdoption'],
                    'railReplay':rec['railReplay'],'formalAccepted':False,'selected':False})

spec=importlib.util.spec_from_file_location('native_source_helper',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources()
for rec in patches:sources.tile(rec['tile'])['selection']['patches'][rec['patch']]=rec['file']
coreguide,pieces,missing=sources.extract(FRAME);assert not missing,missing
assert np.array_equal(np.asarray(coreguide),after),'Colored native cores must replay full guide exactly'

evidence=[]
boxes={'left':[286,280,414,830],'top':[350,216,950,344],'right':[886,280,1014,830],'bottom':[350,766,950,894],
       'inner-left':[382,344,446,766],'inner-top':[414,312,886,376],
       'inner-right':[854,344,918,766],'inner-bottom':[414,734,886,798],
       'G4':[350,280,950,830],'G5':[430,670,950,960],'cross':[350,550,950,1050]}
for name,box in boxes.items():
    p=D/(STEM+'-'+name+'-native.png');assert not p.exists();Image.fromarray(after).crop(box).save(p)
    evidence.append({'name':name,'file':str(p),'sha256':sha(p),'guideBox':box,'dimensions':list(Image.fromarray(after).crop(box).size),'resampling':False})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'bounded_additive_color_finished_pending_native_visual_review','authorization':'Root explicitly authorized approved bounded additive RGB color method after independently viewing v8 geometry.',
        'approvedMethodReference':str(BASE/'r12_c08/color_joint_adoptions.py'),
        'approvedMethodSha256':sha(BASE/'r12_c08/color_joint_adoptions.py'),
        'script':str(Path(__file__)),'scriptSha256':sha(__file__),
        'worldWallRockAdoptionBox':WORLD,'worldApprovedRailBox':coordinated['railWorldBox'],
        'sourceReplay':str(composition_npz),'sourceReplaySha256':sha(composition_npz),'sourceRawImages':[{'version':v,'file':str(p),'sha256':sha(p)} for v,p in rawpaths.items()],
        'rawV6V7V8CompositionExact':True,'fields':fields,'combinedField':str(addnpz),'combinedFieldSha256':sha(addnpz),
        'maximumCumulativeActualRGBChannelChangeFromNativeComposition':maxdelta,
        'maximumCumulativeFloatRGBCorrection':float(np.abs(delta).max()),
        'channelChangeRange':[int((after.astype(np.int16)-before.astype(np.int16)).min()),int((after.astype(np.int16)-before.astype(np.int16)).max())],
        'fieldReplayExact':True,'finalNativeCoreReplayExact':True,'outsideAdoptionPixelsChanged':0,'approvedRailPixelsChanged':0,
        'guide':str(outguide),'guideSha256':sha(outguide),'patches':patches,'evidence':evidence,
        'geometryOperation':'none; all pixel coordinates unchanged','imageResampling':False,'imageBlur':False,'imageBlending':False,'oldImagePixelsMixedIntoRepair':False,
        'profileSmoothingOnly':True,'canonicalSelectionModified':False,'zoneProgressModified':False,'historicalAuditsModified':False,
        'formalAccepted':False,'selected':False,'materialReview':'pending; low-frequency RGB finish cannot remove differences in texture density'}
write(D/(STEM+'.report.json'),report)
print(json.dumps({'report':str(D/(STEM+'.report.json')),'guide':str(outguide),'maximumCumulativeRGBDelta':maxdelta,
                  'exactNativeSourceReplay':True,'exactRGBFieldReplay':True,'exactNativeCoreReplay':True}))
