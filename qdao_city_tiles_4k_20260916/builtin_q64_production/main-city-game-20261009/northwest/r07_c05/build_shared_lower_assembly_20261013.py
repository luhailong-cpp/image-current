from pathlib import Path
import sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent; Z=T.parent; sys.path.insert(0,str(Z))
import production_v2 as p
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
D=T/'bridges/shared-east-lower-02'
base=T/'candidate/r07_c05-candidate-native-rois-final-872df04172946ceb/assembly.json'; m=p.read(base)
candidate=D/'r07_c05-shared-lower-proposal-4096.png'; out=np.array(Image.open(candidate).convert('RGB'))
owners=np.array(Image.open(m['sourceIndex']['file'])); sources=m['nativeSources']; sf=D/'native.png';g=p.read(D/'generation.json')
owners[2673:2796,4059:4096]=len(sources)
sources.append({'id':'shared-east-lower-02','file':str(sf),'sha256':p.sha(sf),'kind':'supplemental_shared_boundary_roi','tileOriginXY':[3469,2200],'worldBox':g['worldBox'],'adoptedSourceROI':[590,473,627,596],'adoptedTileROI':[4059,2673,4096,2796],'generationRecord':ref(D/'generation.json'),'sourceHostFile':g['sourceHostFile'],'sourceHostSha256':g['sourceHostSha256'],'evidence':{'request':g['request'],'receipt':g['toolReceipt'],'prompt':ref(D/'prompt.txt')},'sourceResampled':False})
counts=[]
for i,s in enumerate(sources):
    assert p.sha(s['file'])==s['sha256']
    a=np.array(Image.open(s['file']).convert('RGB')); ys,xs=np.where(owners==i);ox,oy=s['tileOriginXY']
    assert np.array_equal(out[ys,xs],a[ys-oy,xs-ox])
    counts.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactSameWorldNativePixels':True})
assert sum(c['pixelCount'] for c in counts)==4096*4096
index=D/'r07_c05-source-index.png';assert not index.exists();Image.fromarray(owners).save(index)
prior=T/'qa/trial-bottom-floor-cap-02-trimmed/final-current-review.json';review=p.read(prior)
im=Image.fromarray(out); reused=[]
for item in review['internalQA']['entries']:
    crop=im.crop(item['cropLTRB'])
    if item['rotationCCW90']:crop=crop.transpose(Image.Transpose.ROTATE_90)
    assert p.sha(item['file'])==item['sha256']
    assert crop.tobytes()==Image.open(item['file']).convert('RGB').tobytes()
    assert item['visualVerdict']=='passed'
    reused.append({'name':item['name'],'priorCrop':{'file':item['file'],'sha256':item['sha256']},'cropLTRB':item['cropLTRB'],'rotationCCW90':item['rotationCCW90'],'status':'passed_by_exact_pixel_identity','actuallyViewedAgain':False})
old=np.array(Image.open(m['output']['file']).convert('RGB'))
assert np.array_equal(out[:320,:,:],old[:320,:,:]) and np.array_equal(out[:,:320,:],old[:,:320,:])
assembly={'schemaVersion':2,'createdAtUtc':p.now(),'tile':'r07_c05','status':'native_assembly_pending_independent_local_review','output':ref(candidate),'baseManifest':ref(base),'nativeSources':sources,'fixedGridSourceCount':16,'additionalNativeSourceCount':len(sources)-16,'totalNativeSourceCount':len(sources),'sourceIndex':ref(index),'sourceIndexEncoding':'uint8 zero-based nativeSources; nativeXY=tileXY-tileOriginXY','pixelProof':{'status':'passed','checkedPixels':sum(c['pixelCount'] for c in counts),'allPixelsUnmodifiedNativeSamplesAtExactWorldCoordinates':True,'sources':counts},'unchangedInternalQA':{'priorReview':ref(prior),'count':len(reused),'entries':reused},'actualNorthWestBoundaryPixelsUnchanged':True,'sourceResampled':False,'blending':False,'feathering':False,'formalAccepted':False,'currentDeliveredVersionUnchanged':True}
p.write_json(D/'r07_c05-assembly.json',assembly,replace=False)
print({'candidate':str(candidate),'sha256':p.sha(candidate),'sources':len(sources),'exactNativePixels':16777216,'unchangedPassedInternalCrops':len(reused)})
