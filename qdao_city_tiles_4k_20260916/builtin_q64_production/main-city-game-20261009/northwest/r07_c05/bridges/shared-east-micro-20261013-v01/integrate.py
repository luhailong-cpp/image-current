from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, copy
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
Z=OUT.parents[2]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'file':str(p),'sha256':sha(p)}
def write(p,v):
    with Path(p).open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2); f.write('\n')
def save(p,arr):
    assert not p.exists(),str(p)
    Image.fromarray(arr).save(p)
def rgb(p): return np.array(Image.open(p).convert('RGB'))
def verify(r):
    assert sha(r['file'])==r['sha256'],r['file']
    return Path(r['file'])

base_manifest=Z/'r07_c05/bridges/shared-east-lower-03/r07_c05-assembly.json'
bm=read(base_manifest)
assert bm['output']['sha256']=='618884ddac30a22c5aa5e670319742c96efe4a3c21927ca6605ecdd9a4cc0a19'
base=rgb(verify(bm['output']))
owner=np.array(Image.open(verify(bm['sourceIndex'])))
assert owner.shape==(4096,4096)
source_dir=Z/'r07_c06/repair-batches/shared-west-micro-01'
gen=read(source_dir/'generation.json')
assert gen['native']['sha256']=='664c036144808c039241690842a4a915709f6ca44f95e054049ff984e8ca5616'
native=rgb(verify(gen['native']))
assert native.shape==(1254,1254,3)
assert gen['nativeWorldBox']==[19853,26776,21107,28030]
assert gen['tileOriginXY']==[-627,2200]
coords=read(Z/'r07_c05/coordinates.json')
tileworld=coords['tileWorldBox']
assert tileworld==[16384,24576,20480,28672]
origin=[gen['nativeWorldBox'][i]-tileworld[i] for i in range(2)]
assert origin==[3469,2200]
assert sha(gen['sourceHostFile'])==gen['native']['sha256']
verify(gen['request']); verify(gen['parameters'])
rois=[[617,382,627,408],[617,1077,627,1103]]
current=base.copy(); mask=np.zeros((4096,4096),bool)
tiles=[]
sources=copy.deepcopy(bm['nativeSources'])
assert len(sources)==23
sources.append({'id':'shared-east-micro-20261013-v01','file':gen['native']['file'],'sha256':gen['native']['sha256'],
    'tileOriginXY':origin,'worldBox':gen['nativeWorldBox'],'adoptedSourceROIs':rois,
    'generationRecord':ref(source_dir/'generation.json'),'sourceHostFile':gen['sourceHostFile'],
    'sourceHostSha256':gen['native']['sha256'],'sourceResampled':False,
    'evidence':{'request':gen['request'],'parameters':gen['parameters'],'prompt':ref(source_dir/'prompt.txt')}})
for r in rois:
    x0,y0,x1,y1=r; t=[x0+origin[0],y0+origin[1],x1+origin[0],y1+origin[1]]
    a,b,c,d=t; current[b:d,a:c]=native[y0:y1,x0:x1]; owner[b:d,a:c]=23; mask[b:d,a:c]=True; tiles.append(t)
sources[-1]['adoptedTileROIs']=tiles
assert int(mask.sum())==520 and np.array_equal(current[~mask],base[~mask])
output=OUT/'r07_c05-combined-shared-micro-4096.png'; save(output,current)
index=OUT/'r07_c05-source-index.png'; save(index,owner)
proof=[]
for i,s in enumerate(sources):
    src=rgb(verify(s)); ys,xs=np.where(owner==i); ox,oy=s['tileOriginXY']; sx=xs-ox; sy=ys-oy
    assert len(xs)==0 or (sx.min()>=0 and sy.min()>=0 and sx.max()<src.shape[1] and sy.max()<src.shape[0])
    assert np.array_equal(current[ys,xs],src[sy,sx]),s['id']
    proof.append({'sourceIndex':i,'pixelCount':len(xs),'exactSameWorldNativePixels':True})
assert sum(p['pixelCount'] for p in proof)==4096*4096
qa=[]
for e in bm['internalQA']['entries']:
    e=copy.deepcopy(e); x0,y0,x1,y1=e['cropLTRB']
    assert np.array_equal(current[y0:y1,x0:x1],base[y0:y1,x0:x1])
    e['unchangedFromImmediateBase']=True
    if e['status']=='pending_changed_crop_review':
        c=current[y0:y1,x0:x1]
        if e['rotationCCW90']: c=np.rot90(c)
        f=OUT/(e['name']+'.png'); save(f,c); e['currentCrop']=ref(f)
    qa.append(e)
right_manifest=Z/'r07_c06/candidate/native-overlays-20261013-v10.json'
rm=read(right_manifest); right=rgb(verify(rm['candidate']))
frame=np.concatenate([current[2200:3454,3469:4096],right[2200:3454,0:627]],axis=1)
assert frame.shape==(1254,1254,3)
target=rgb(source_dir/'edit-target.png')
assert np.array_equal(base[2200:3454,3469:4096],target[:,:627])
crop_records=[]
for y in (395,1090):
    box=[550,y-64,704,y+64]
    for label,img in [('before',target),('after',frame)]:
        f=OUT/f'micro-y{y}-{label}-native.png'; x0,y0,x1,y1=box; save(f,img[y0:y1,x0:x1]); crop_records.append({'gapY':y,'label':label,'frameCropLTRB':box,**ref(f)})
for r in rois:
    x0,y0,x1,y1=r
    assert np.array_equal(frame[y0:y1,x0:639],native[y0:y1,x0:639]),'Both halves must use same native source at ROI'
record={'schemaVersion':2,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c05',
  'status':'micro_integrated_pending_local_visual_review_and_remaining_shared_repairs','output':ref(output),
  'baseManifest':ref(base_manifest),'nativeSources':sources,'fixedGridSourceCount':16,'additionalNativeSourceCount':8,'totalNativeSourceCount':24,
  'sourceIndex':ref(index),'sourceIndexEncoding':bm['sourceIndexEncoding'],
  'pixelProof':{'status':'passed','checkedPixels':4096*4096,'sources':proof},
  'changedPixels':int(np.any(current!=base,axis=2).sum()),'adoptedNativePixelCount':520,'outsideAdoptedROIsUnchanged':True,
  'internalQA':{'priorReview':bm['internalQA']['priorReview'],'entries':qa,'all33CropsUnchangedFromImmediateBase':True},
  'northAndWest160PixelBoundaryBandsUnchanged':bool(np.array_equal(current[:160],base[:160]) and np.array_equal(current[:,:160],base[:,:160])),
  'microJointReview':{'rightCandidate':rm['candidate'],'rightRegistry':ref(right_manifest),'nativeCropImages':crop_records,'visualStatus':'pending'},
  'sourceResampled':False,'blending':False,'recolored':False,'formalAccepted':False,'wholeZoneComplete':False,
  'eastBoundaryRemainingDefects':[{'frameY':[215,223],'status':'deferred_unpassed'},{'frameY':[727,756],'status':'deferred_after_two_failed_repairs_unpassed'}],
  'remainingDefectCoordinatesRelativeToSharedFrame':True}
write(OUT/'r07_c05-assembly.json',record)
print(json.dumps({'output':record['output'],'sourceIndex':record['sourceIndex'],'sourceCount':24,'checkedPixels':4096*4096,'adopted':520,'changed':record['changedPixels'],'all33InternalUnchanged':True},indent=2))
