"""Read-only native sources; hypothetical integer-translation QA only.

No native metadata, source coordinates, generation records, plan or tile is edited.
Only original pixels may appear in diagnostic joins. No interpolation or blending.
"""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
A_PATH=ROOT/'native/r03_c02_s01_s04_v01.png'
B_PATH=ROOT/'native/r03_c03_s01_s01_v01.png'
N=1254

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j): p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def integral(a):
    return np.pad(np.cumsum(np.cumsum(np.sum(a.astype(np.int64)**2,axis=2),axis=0),axis=1),((1,0),(1,0)))
def boxsum(ii,x0,y0,x1,y1): return ii[y1,x1]-ii[y0,x1]-ii[y1,x0]+ii[y0,x0]
def fftcorr(a,b):
    shape=tuple(1 << int(v-1).bit_length() for v in (a.shape[0]+b.shape[0]-1,a.shape[1]+b.shape[1]-1))
    total=None
    for c in range(3):
        fa=np.fft.rfft2(a[:,:,c],s=shape)
        fb=np.fft.rfft2(b[::-1,::-1,c],s=shape)
        conv=np.fft.irfft2(fa*fb,s=shape)
        if total is None: total=conv
        else: total+=conv
    return np.rint(total).astype(np.int64)

def overlap(a,b,dx,dy):
    ay0,ay1=max(0,-dy),min(N,N-dy)
    by0,by1=max(0,dy),min(N,N+dy)
    return a[ay0:ay1,1024-dx:],b[by0:by1,:230+dx]

def true_overlap_search(a,b):
    # A's right290 pixels include all pixels that could overlap B for dx +-60.
    aa=a[:,964:];bb=b[:,:290]
    corr=fftcorr(aa,bb);ia,ib=integral(aa),integral(bb)
    mse=np.zeros((121,121));sse=np.zeros((121,121),dtype=np.int64)
    for iy,dy in enumerate(range(-60,61)):
        ay0,ay1=max(0,-dy),min(N,N-dy)
        by0,by1=max(0,dy),min(N,N+dy)
        for ix,dx in enumerate(range(-60,61)):
            lag=60-dx; width=230+dx
            cross=corr[N-1-dy,289+lag]
            s=boxsum(ia,lag,ay0,290,ay1)+boxsum(ib,0,by0,width,by1)-2*cross
            assert s>=0
            sse[iy,ix]=s;mse[iy,ix]=s/(3*width*(N-abs(dy)))
    order=np.argsort(mse,axis=None)[:12]
    top=[]
    for k in order:
        iy,ix=np.unravel_index(k,mse.shape);dx,dy=int(ix-60),int(iy-60)
        aa,bb=overlap(a,b,dx,dy);err=aa.astype(np.int64)-bb.astype(np.int64)
        assert int(np.sum(err**2))==int(sse[iy,ix]),'FFT score disagrees with exact pixels'
        top.append({'dx':dx,'dy':dy,'mseRGB':float(mse[iy,ix]),'maeRGB':float(np.abs(err).mean()),'overlapSize':[aa.shape[1],aa.shape[0]],'sseRGB':int(sse[iy,ix])})
    np.save(HERE/'true-overlap-mse-grid.npy',mse)
    return top

def fixed_band_search(a,b,y0,y1):
    # Same global evaluation pixels for every shift: B x60..170, y y0..y1.
    # Search A windows with offsets (60-dx,60-dy) inside this right230 region.
    target=b[y0:y1,60:170]
    search=a[y0-60:y1+60,1024:1254]
    h,w=target.shape[:2];corr=fftcorr(search,target)
    ii=integral(search);sums=ii[h:,w:]-ii[:-h,w:]-ii[h:,:-w]+ii[:-h,:-w]
    cross=corr[h-1:search.shape[0],w-1:search.shape[1]]
    sse=sums+np.sum(target.astype(np.int64)**2)-2*cross
    iy,ix=np.unravel_index(sse.argmin(),sse.shape)
    dx,dy=60-int(ix),60-int(iy)
    piece=search[iy:iy+h,ix:ix+w]
    assert int(np.sum((piece.astype(np.int64)-target.astype(np.int64))**2))==int(sse[iy,ix])
    return {'fixedReferenceCrop':[60,y0,170,y1],'dx':dx,'dy':dy,'mseRGB':float(sse[iy,ix]/target.size),'maeRGB':float(np.abs(piece.astype(int)-target.astype(int)).mean())}

def minimum_path(cost):
    h,w=cost.shape;back=np.zeros((h,w),dtype=np.int8);previous=cost[0].copy();inf=np.int64(10**13);x=np.arange(w)
    for y in range(1,h):
        choices=np.stack((previous,np.r_[inf,previous[:-1]],np.r_[previous[1:],inf]))
        ix=choices.argmin(axis=0);previous=cost[y]+choices[ix,x];back[y]=np.array([0,-1,1],dtype=np.int8)[ix]
    path=np.empty(h,dtype=np.int32);path[-1]=previous.argmin();total=int(previous[path[-1]])
    for y in range(h-1,0,-1):path[y-1]=path[y]+back[y,path[y]]
    return path,total

def diagnostic(a,b,dx,dy,name):
    aa,bb=overlap(a,b,dx,dy)
    cost=np.sum((aa.astype(np.int64)-bb.astype(np.int64))**2,axis=2)
    path,total=minimum_path(cost)
    ay0,ay1=max(0,-dy),min(N,N-dy);by0,by1=max(0,dy),min(N,N+dy)
    off=1024-dx;h=aa.shape[0];w=off+N
    joined=np.zeros((h,w,3),dtype=np.uint8);ids=np.zeros((h,w),dtype=np.uint8)
    joined[:,:N]=a[ay0:ay1];ids[:,:N]=1
    for y in range(h):
        start=off+int(path[y]);joined[y,start:]=b[by0+y,start-off:];ids[y,start:]=2
    # Validate both sides map to exact source pixels at integer offsets.
    for y in range(h):
        xx=np.flatnonzero(ids[y]==1);assert np.array_equal(joined[y,xx],a[ay0+y,xx])
        xx=np.flatnonzero(ids[y]==2);assert np.array_equal(joined[y,xx],b[by0+y,xx-off])
    d=HERE/name;d.mkdir(exist_ok=True)
    Image.fromarray(joined).save(d/'joined.png');Image.fromarray(ids).save(d/'source-id.png')
    gx0=7053+dx;gy0=8077+max(0,dy)
    crops=[]
    split=h//2
    for key,y0,y1 in [('upper',0,split),('lower',split,h)]:
        box=[7953-gx0,y0,8453-gx0,y1]
        p=d/f'{key}.100pct.png';Image.fromarray(joined).crop(box).save(p)
        crops.append({'file':str(p),'sha256':sha(p),'cropFromJoined':box,'globalHypotheticalBox':[7953,gy0+y0,8453,gy0+y1]})
    Image.fromarray(aa).save(d/'west-overlap.png');Image.fromarray(bb).save(d/'east-overlap.png')
    r={'name':name,'diagnosticOnly':True,'originalNominalWestNativeBox':[7053,8077,8307,9331],
       'originalNominalEastNativeBox':[8077,8077,9331,9331],
       'hypotheticalTranslation':{'dx':dx,'dy':dy,'appliedTo':'west only'},
       'hypotheticalWestBox':[7053+dx,8077+dy,8307+dx,9331+dy],
       'actualComparedGlobalIntersection':[8077,8077+max(dy,0),8307+dx,9331+min(dy,0)],
       'comparedOverlapSize':[aa.shape[1],aa.shape[0]],
       'maeRGB':float(np.abs(aa.astype(int)-bb.astype(int)).mean()),
       'mseRGB':float(cost.mean()/3),'pathCostSquaredRGB':total,'pathLocal':path.tolist(),
       'joined':str(d/'joined.png'),'joinedSha256':sha(d/'joined.png'),
       'sourceIds':str(d/'source-id.png'),'sourceIdSha256':sha(d/'source-id.png'),
       'sourcePixelProvenanceVerified':True,'noInterpolation':True,'noRotation':True,'noWarp':True,'noBlend':True,'noColorEdit':True,
       'generationAndGlobalBoxRecordsModified':False,'status':'pending-100pct-visual-review','evidence':crops}
    write(d/'record.json',r)
    return {'name':name,'dx':dx,'dy':dy,'record':str(d/'record.json'),'joinedSha256':r['joinedSha256'],'maeRGB':r['maeRGB']}

def main():
    assert sha(A_PATH)=='96d93b9309099487e54aff6adfc2fe1dcee9ccd4401c892ade7ce21437f5ddb9'
    assert sha(B_PATH)=='43cc2542995ab18542e1f3b4b2182c3fbe243d45b4e5637a96ee5b91d8feb643'
    a,b=[np.array(Image.open(p).convert('RGB')) for p in [A_PATH,B_PATH]]
    top=true_overlap_search(a,b)
    bands={name:fixed_band_search(a,b,*ys) for name,ys in [('all-common',(60,1194)),('roof',(60,650)),('caps-eave',(650,925)),('timber',(925,1194))]}
    shifts=[('nominal',0,0),('best-true-overlap',top[0]['dx'],top[0]['dy'])]
    for name,r in bands.items():
        if not any((dx,dy)==(r['dx'],r['dy']) for _,dx,dy in shifts):shifts.append(('best-'+name,r['dx'],r['dy']))
    joins=[diagnostic(a,b,dx,dy,name) for name,dx,dy in shifts]
    result={'diagnosticOnly':True,'searchBounds':{'dx':[-60,60],'dy':[-60,60],'integerSteps':1,'candidates':14641},
            'nominalBoxesUnmodified':True,'sources':[{'file':str(p),'sha256':sha(p)} for p in [A_PATH,B_PATH]],
            'trueOverlapTop12':top,'fixedCommonBandBest':bands,'diagnosticJoins':joins,'script':str(Path(__file__).resolve()),'scriptSha256':sha(__file__)}
    write(HERE/'search.json',result)
    print(json.dumps({'top':top[:3],'bands':bands,'joins':joins}))

if __name__=='__main__': main()
