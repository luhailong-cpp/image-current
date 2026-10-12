from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np, hashlib, json
ROOT=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r03_c10')
REPAIR=ROOT/'repairs'/'umbrella-tint-v1'
QA=ROOT/'qa'/'full-audit'/'tint-v2'
QA.mkdir(parents=True,exist_ok=True)
PREV=ROOT/'candidate'/'r03_c10-4096-candidate-v1.png'
OUT=ROOT/'candidate'/'r03_c10-4096-candidate-v2.png'
assert not OUT.exists(), 'Do not overwrite an existing version.'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p): return {'file':str(p),'sha256':sha(p)}
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=Image.open(PREV).convert('RGB')
target=Image.open(REPAIR/'target-native.png').convert('RGB')
repair=Image.open(REPAIR/'native-result.png').convert('RGB')
assert base.size==(4096,4096)
assert target.size==repair.size==(1254,1254)
box=[1421,128,2675,1382]
assert base.crop(box).tobytes()==target.tobytes(), 'Target must exactly equal the recorded source crop.'
roi=[390,230,865,1145]
feather_x=96
feather_y=32
yy,xx=np.indices((1254,1254))
def smooth(v):
 v=np.clip(v,0,1); return v*v*(3-2*v)
dx=np.minimum(xx-roi[0],roi[2]-1-xx)
dy=np.minimum(yy-roi[1],roi[3]-1-yy)
alpha=smooth(dx/feather_x)*smooth(dy/feather_y)
mask_array=np.rint(alpha*255).astype(np.uint8)
mask=Image.fromarray(mask_array,'L')
maskpath=REPAIR/'blend-mask-local-1254.png'
assert not maskpath.exists()
mask.save(maskpath)
# Native per-pixel alpha compositing only; no resampling, warping, painting, or color transform.
local=Image.composite(repair,target,mask)
v2=base.copy(); v2.paste(local,(box[0],box[1]))
v2.save(OUT)
aa=np.array(base); bb=np.array(v2)
changed=np.any(aa!=bb,axis=2)
xs=np.where(changed)[1]; ys=np.where(changed)[0]
changed_box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
border_results={}
for k,b in {'top':[0,0,4096,115],'bottom':[0,3981,4096,4096],'left':[0,0,115,4096],'right':[3981,0,4096,4096]}.items():
 p=base.crop(b).tobytes(); q=v2.crop(b).tobytes()
 border_results[k]={'widthPixels':115,'byteIdentical':p==q,'v1RawRGBSha256':hashlib.sha256(p).hexdigest(),'v2RawRGBSha256':hashlib.sha256(q).hexdigest()}
 assert p==q
outside=np.ones(changed.shape,dtype=bool)
global_roi=[box[0]+roi[0],box[1]+roi[1],box[0]+roi[2],box[1]+roi[3]]
outside[global_roi[1]:global_roi[3],global_roi[0]:global_roi[2]]=False
assert not np.any(changed[outside])
def seam_stats(arr,x,y1,y2):
 a=arr.astype(np.float32)
 jump=np.abs(a[y1:y2,x]-a[y1:y2,x-1])
 local=np.abs(np.diff(a[y1:y2,x-16:x+17],axis=1))
 neighbor=np.concatenate([local[:,:15],local[:,16:]],axis=1)
 return {'meanAbsoluteAdjacentRGBJump':float(jump.mean()),'neighbor32ColumnMeanAbsoluteRGBJump':float(neighbor.mean()),'jumpToNearbyRatio':float(jump.mean()/max(neighbor.mean(),1e-6)),'meanRightMinusLeftRGB':(a[y1:y2,x]-a[y1:y2,x-1]).mean(axis=0).tolist()}
before=seam_stats(aa,2048,384,1024); after=seam_stats(bb,2048,384,1024)
metrics={'primarySeamTileX':2048,'evaluatedTileYHalfOpen':[384,1024],'before':before,'after':after,'meanJumpReductionPercent':100*(1-after['meanAbsoluteAdjacentRGBJump']/before['meanAbsoluteAdjacentRGBJump']),'changedPixelCount':int(changed.sum()),'changedPixelBoundingBoxTileXYXY':changed_box,'outer115PixelStrips':border_results,'allPixelsOutsideROIByteIdentical':bool(not np.any(changed[outside]))}
write(QA/'metrics.json',metrics)
for label,im in [('before',base),('after',v2)]:
 im.crop([1792,256,2304,1344]).save(QA/(label+'-seam-native-512x1088.png'))
 im.crop([1747,294,2350,1337]).save(QA/(label+'-roi-transition-native-603x1043.png'))
 im.crop(box).save(QA/(label+'-target-native-1254.png'))
 im.crop([1792,992,2304,1056]).save(QA/(label+'-horizontal-y1024-native.png'))
 im.crop([1792,1075,2304,1291]).save(QA/(label+'-lower-rib-rim-native.png'))
preview=v2.copy(); preview.thumbnail((1024,1024)); preview.save(QA/'candidate-v2-preview-only.png')
manifest={'file':str(OUT),'sha256':sha(OUT),'dimensions':list(v2.size),'classification':'4096 composite of selected native cores plus native builtin local repair; not single native 4K generation','previousCandidate':rec(PREV),'previousCandidateManifest':rec(PREV.with_suffix('.manifest.json')),'repairNative':{**rec(REPAIR/'native-result.png'),'measuredDimensions':list(repair.size),'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'unknownReason':'Builtin receipt does not disclose verified model or quality fields.'},'prompt':rec(REPAIR/'prompt.txt'),'request':rec(REPAIR/'request.json'),'receipt':rec(REPAIR/'receipt.json'),'referenceEditTarget':rec(REPAIR/'target-native.png'),'referenceDerivation':rec(REPAIR/'target-native.derivation.json'),'compositing':{'script':rec(Path(__file__)),'operation':'Pillow Image.composite(result,target,L-mask) then unscaled paste at source crop origin','sourceCropBoxTileXYXY':box,'mask':rec(maskpath),'maskDimensions':[1254,1254],'roiLocalXYXYHalfOpen':roi,'roiTileXYXYHalfOpen':global_roi,'featherPixelsX':feather_x,'featherPixelsY':feather_y,'maskFormula':'8-bit round(255*smoothstep(min(x-x0,x1-1-x)/96)*smoothstep(min(y-y0,y1-1-y)/32)), smoothstep(t)=clip(t,0,1)^2*(3-2*clip(t,0,1))','nativePixelsResized':False,'geometricTransform':None,'syntheticPainting':False},'verificationMetrics':rec(QA/'metrics.json'),'formalAccepted':False,'status':'pending visual review of internal repaired seam','externalSeamsChecked':False,'createdAt':datetime.now(timezone.utc).isoformat()}
write(OUT.with_suffix('.manifest.json'),manifest)
print(json.dumps({'candidate':str(OUT),'metrics':metrics},indent=2))

