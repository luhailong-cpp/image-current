from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent
Q = R / 'qa/full-resume-20261012-v4-color'
NOW = datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
native = read(R/'native-selected-before-color-20261012-v2.json')
color = read(R/'colorpass-selected-20261012-v1.json')
manifest = read(Q/'manifest.json')
assert len(manifest['evidence']) == 33 and manifest['selectedCount'] == 16
proof = []
for k,p in color['patches'].items():
    src=R/native['patches'][k]; out=R/p; field=out.with_name(k+'-color-field.npz')
    a=np.asarray(Image.open(src).convert('RGB'),dtype=np.float32)
    b=np.asarray(Image.open(out).convert('RGB'))
    z=np.load(field); grid=z['additiveGridRgb']; n=grid.shape[0]
    q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,n-1)
    lo=np.floor(q).astype(int); hi=np.minimum(lo+1,n-1); w=q-lo
    top=grid[lo[:,None],lo[None,:]]*(1-w[None,:,None])+grid[lo[:,None],hi[None,:]]*w[None,:,None]
    bot=grid[hi[:,None],lo[None,:]]*(1-w[None,:,None])+grid[hi[:,None],hi[None,:]]*w[None,:,None]
    f=(top*(1-w[:,None,None])+bot*w[:,None,None]).astype(np.float32)
    f*=1-z['safetyProtectionY'][:,None,None]*(1-z['safetyWeightX'][None,:,None])
    rebuilt=np.uint8(np.clip(np.rint(a+np.clip(f,-24,24)),0,255))
    assert np.array_equal(rebuilt,b)
    maximum=int(np.abs(b.astype(np.int16)-a.astype(np.int16)).max())
    assert maximum<=24 and np.array_equal(a[499:755,499:755],b[499:755,499:755])
    if k[1]=='4': assert np.array_equal(a[883:],b[883:])
    gen=read(str(src)+'.generation.json')
    assert Image.open(src).size==(1254,1254)
    proof.append(dict(patch=k,native=str(src),nativeSha256=sha(src),generationRecord=str(src)+'.generation.json',generationRecordSha256=sha(str(src)+'.generation.json'),output=str(out),outputSha256=sha(out),field=str(field),fieldSha256=sha(field),everyOutputPixelReconstructed=True,maximumActualChannelChange=maximum,unchangedCoreCenter=True,protectedSouth256Unchanged=(True if k[1]=='4' else None),actualModel=gen.get('actualModel'),actualQuality=gen.get('actualQuality')))
proofpath=Q/'color-field-proof.json'
write(proofpath,dict(createdAt=NOW,formula='uint8(clip(rint(native + clip(expanded_saved_npz_field * saved_safety_weights, -24, 24)),0,255))',resampling=False,imageBlur=False,imagePixelBlend=False,coordinateShift=[0,0],all16OutputsReconstructed=True,records=proof,script=str(Path(__file__)),scriptSha256=sha(__file__)))
reviews=[]
for rec in manifest['evidence']:
    assert sha(rec['file'])==rec['sha256']
    item=dict(file=rec['file'],sha256=rec['sha256'],reviewedAt=NOW,reviewMethod='view_image original resolution, all 24 internal seam strips and nine crossings',geometry='pass',layout='pass',materials='pass',daylightStyle='pass',color='pass_with_minor_natural_source_texture_variation',blockingDefects=[],notes='Stone grout, canopy contours, roof course and ridge shadows connect; additive color field reduces tonal steps without spatial changes.')
    reviews.append(item)
    rec['visualReview']='pass';rec['ownerReview']=item
    rp=Path(str(rec['file'])+'.derivation.json')
    if rp.exists():
        d=read(rp);d['visualReview']='pass';d['ownerReview']=item;write(rp,d)
candidate=Path(manifest['candidate'])
reviewpath=Q/'owner-review.json'
write(reviewpath,dict(createdAt=NOW,tile='r09_c09',candidate=str(candidate),candidateSha256=sha(candidate),dimensions=[4096,4096],selectedCount=16,internalSeamCount=24,internalCrossingCount=9,all33ViewedAt100Percent=True,all33Passed=True,internalReady=True,internalGeometryReady=True,formalAccepted=False,externalStatus='Available sources reviewed separately; missing neighbors prevent formal acceptance',colorProof=str(proofpath),reviews=reviews))
manifest.update(internalReady=True,formalAccepted=False,ownerReview=str(reviewpath),ownerReviewSha256=sha(reviewpath),candidateSha256=sha(candidate))
write(Q/'manifest.json',manifest)
snapshot=R/'selected-patches-before-final-20261012.json'
assert not snapshot.exists()
shutil.copy2(R/'selected-patches.json',snapshot)
selection=dict(tile='r09_c09',patches=color['patches'],status='internal_ready_external_pending',internalReady=True,internalGeometryReady=True,formalAccepted=False,updatedAt=NOW,nativeSelectionSnapshot=str(R/'native-selected-before-color-20261012-v2.json'),nativeSelectionSha256=sha(R/'native-selected-before-color-20261012-v2.json'),boundedColorManifest=str(R/'colorpass-selected-20261012-v1.json'),boundedColorManifestSha256=sha(R/'colorpass-selected-20261012-v1.json'),colorLimitRgb=24,actualModel=None,actualQuality=None,qaManifest=str(Q/'manifest.json'),ownerReview=str(reviewpath),candidate=str(candidate),candidateSha256=sha(candidate),dimensions=[4096,4096],coreCrop=[115,115,1139,1139],pixelCoverage=16777216,selectionBeforeFinal=str(snapshot))
write(R/'selected-patches-final-20261012-v1.json',selection)
write(R/'selected-patches.json',selection)
progress=dict(tile='r09_c09',createdAt=NOW,selectedCount=16,generatedNativeCount=len(list((R/'native').glob('*.png.generation.json'))),generatedJointRepairCount=len(list((R/'repairs').glob('*.png.generation.json'))),remainingPositions=[],complete4kCount=1,internalReady4kCount=1,formalAcceptedCount=0,internalReady=True,formalAccepted=False,internalQaReviewed=33,candidate=str(candidate),candidateSha256=sha(candidate),selection=str(R/'selected-patches.json'),selectionSha256=sha(R/'selected-patches.json'),colorProof=str(proofpath),pendingExternal=['north','east','west','southwest outer crossing','southeast outer crossing'],nextStep='Refresh tile-local available external QA, then produce r08_c09 bottom row northward.',actualModel=None,actualQuality=None)
write(R/'progress-20261012-final-v1.json',progress)
write(R/'progress.json',progress)
for d in sorted((R/'processed').glob('jointpass-20261012-v*')):
    rp=d/'rejection-20261012-final.json'
    if not rp.exists():write(rp,dict(createdAt=NOW,status='rejected_not_selected',reason='Joint native replacement or binary adoption shifted intact fixed contours or produced unnatural cutoff/tone boundaries. Actual-core p23-v2 and p34-v2 native refreshes supersede these attempts; preserve all raw sources and candidates.',selected=False))
write(R/'local-handoff-20261012.json',dict(createdAt=NOW,tile='r09_c09',internalReady=True,formalAccepted=False,selection=str(R/'selected-patches.json'),nativeSnapshot=selection['nativeSelectionSnapshot'],candidate=str(candidate),candidateSha256=sha(candidate),qa=str(Q),colorProof=str(proofpath),nativeGenerator='builtin image_gen working; historical permission errors not current blockers',actualModel=None,actualQuality=None,nextExclusiveTile='r08_c09',pending='External neighbors missing; do not claim formal acceptance'))
print(json.dumps(progress,indent=2))
