from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
import numpy as np
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parent.parent
E = R/'work-r03_c02/qa/e3-repair'
N = R/'work-r04_c03/joint-north'
S = R/'work-r04_c04/joint-west/final-v3'
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb = lambda p: np.asarray(Image.open(p).convert('RGB'))
ids = lambda p: np.asarray(Image.open(p))
def info(p, **kw): return {'file': str(p), 'sha256': sha(p), **kw}
def save(a,p): Image.fromarray(a).save(p)
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

em, nm, sm = read(E/'e3-proposal-v09.assembly.json'), read(N/'joint-assembly.json'), read(S/'joint-assembly.json')
assert em['candidate']['sha256']=='4d5b028fcf8c95e61381fb8260a26e59c0f56d8e4529623df3967c9bc23c038b'
for v in [em['candidate'],em['base']]+nm['inputBaselines']+sm['artifacts']:
    assert sha(v['file'])==v['sha256'],v['file']
base=rgb(em['base']['file']); e3=rgb(em['candidate']['file']); ei=ids(em['sourceIdFile'])
north=rgb(N/'r03_c03.joint-proposal.png'); ni=ids(N/'r03_c03.joint-source-id.png')
south=rgb(S/'r04_c03.joint-proposal.png'); si=ids(S/'r04_c03.source-id.png')
mask=np.isin(ei,[201,202]); north_changed=np.any(north!=base,axis=2)
assert mask.sum()==459374
assert not np.any(mask & north_changed)
assert np.array_equal(e3[~mask],base[~mask])
out=north.copy(); oi=ni.astype(np.uint16)
out[mask]=e3[mask]; oi[mask]=ei[mask]
assert np.array_equal(out[-115:],north[-115:])
assert np.array_equal(south[:115],rgb(N/'r04_c03.joint-proposal.png')[:115])
sources={s['jointSourceId']:s for s in sm['sources']}
for s in nm['sources']:
    assert sources[s['jointSourceId']]['sha256']==s['sha256']
for key in [201,202]:
    assert key not in sources
    s=em['sources'][str(key)].copy(); s.update(jointSourceId=key,tile='r03_c03',actualModel=None,actualQuality=None,route='builtin',nativeScaleResampled=False)
    s['generationRecord']=s['file']+'.generation.json';s['generationRecordSha256']=sha(s['generationRecord']);sources[key]=s

cache={}
def proof(a, im, origin, name):
    count=0; contributions=[]
    for key in np.unique(im):
        s=sources[int(key)]
        if key not in cache:
            assert sha(s['file'])==s['sha256']
            assert sha(s['generationRecord'])==s['generationRecordSha256']
            cache[key]=rgb(s['file'])
        yy,xx=np.nonzero(im==key); bx,by,ex,ey=s['globalNativeBox']; sx=xx+origin[0]-bx;sy=yy+origin[1]-by
        assert cache[key].shape==(ey-by,ex-bx,3)
        assert np.all((sx>=0)&(sx<ex-bx)&(sy>=0)&(sy<ey-by))
        assert np.array_equal(a[yy,xx],cache[key][sy,sx]),(name,int(key))
        count+=len(xx);contributions.append({'sourceId':int(key),'pixels':len(xx)})
    assert count==a.shape[0]*a.shape[1]
    return {'name':name,'pixelsVerified':count,'mismatchedPixels':0,'contributions':contributions}
ep=proof(e3,ei,[8192,8192],'independent-e3-input')
npf=proof(out,oi,[8192,8192],'combined-r03_c03')
sp=proof(south,si,[8192,12288],'unchanged-south-final-v3')
candidate=D/'r03_c03.joint-proposal.png';sourceid=D/'r03_c03.source-id.png'
save(out,candidate);save(oi,sourceid)
assert np.array_equal(rgb(candidate),out) and np.array_equal(ids(sourceid),oi)
diagnostics=[]
def crop(name,a,box):
    p=D/(name+'.100pct.png');save(a,p);diagnostics.append(info(p,globalBox=box,nativeScale=1))
band=np.concatenate([out[-320:],south[:320]],axis=0)
for i in range(8):
    crop('south-boundary-segment-%02d'%(i+1),band[:,i*512:(i+1)*512],[8192+i*512,11968,8192+(i+1)*512,12608])
for i in range(1,4):
    x=i*1024;crop('south-boundary-cross-%d'%i,band[:,x-230:x+230],[8192+x-230,11968,8192+x+230,12608])
for name,box in [('e3-upper',[8192,8892,8700,9892]),('e3-lower',[8192,9892,8700,10822]),('center-left-quadrants',[11776,11776,12288,12800])]:
    x,y,x2,y2=box
    if name=='center-left-quadrants':
        arr=np.concatenate([out[-512:,-512:],south[:512,-512:]],axis=0)
    else: arr=out[y-8192:y2-8192,x-8192:x2-8192]
    crop(name,arr,box)

changed=np.any(out!=base,axis=2)
result={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'E3-and-left-column-south-boundary-integrated-awaiting-independent-visual-review','formalAccepted':False,'candidate':info(candidate,size=[4096,4096],globalBox=[8192,8192,12288,12288]),'sourceIdMap':info(sourceid),'sources':list(sources.values()),'inputs':[info(E/'e3-proposal-v09.assembly.json'),info(N/'joint-assembly.json'),info(S/'joint-assembly.json')],'base':em['base'],'southCompanion':sm['artifacts'][0],'proofs':[ep,npf,sp],'e3SourcePixels':int(mask.sum()),'jointNorthRGBChangedPixels':int(north_changed.sum()),'e3AndNorthMaskIntersection':0,'changedRGBPixelsFromV5':int(changed.sum()),'southCompanionTop115UnchangedFromJointNorth':True,'candidateBottom115UnchangedFromJointNorth':True,'method':'exact native pixels selected by existing two disjoint hard masks; no geometric or color transformation','resampled':False,'feathered':False,'painted':False,'diagnostics':diagnostics,'script':info(Path(__file__)),'limitations':['West edge against r03_c02 still fails existing lantern geometry; no west-edge acceptance.','Whole 2x2 four-tile center awaits right column final proposals.','Independent local E3 visual check passed before merge; boundary visual check follows.'],'originalCandidateOrIndexModified':False}
write(D/'joint-assembly.json',result)
write(D/'mechanical-check.json',{k:result[k] for k in ['createdAt','proofs','e3SourcePixels','e3AndNorthMaskIntersection','changedRGBPixelsFromV5','southCompanionTop115UnchangedFromJointNorth','candidateBottom115UnchangedFromJointNorth','resampled','feathered','painted','formalAccepted']})
print(json.dumps({'candidate':result['candidate'],'proofPixels':sum(p['pixelsVerified'] for p in result['proofs']),'e3SourcePixels':result['e3SourcePixels'],'overlapPixels':0,'diagnosticCount':len(diagnostics)}))
