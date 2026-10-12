"""Copy recorded, already blended native repair contexts without resampling."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
import pipeline as p

spec=p.read(sys.argv[1]);tile=spec['tile'];p.validate_tile(tile)
out=p.owned_path(p.ROOT/tile/spec['outputDirectory']);out.mkdir(parents=True,exist_ok=True)
base=Path(spec['baseCandidate']);a=np.array(Image.open(base).convert('RGB'));original=a.copy()
assert a.shape==(4096,4096,3)
combined=np.zeros((4096,4096),bool);records=[]
for item in spec['contexts']:
    L,T,R,B=item['tileBox'];assert R-L==B-T==1254 and 0<=L<R<=4096 and 0<=T<B<=4096
    raw=np.array(Image.open(item['derivedFile']).convert('RGB'))
    mask=np.array(Image.open(item['supportFile']).convert('L'))>0
    assert raw.shape==(1254,1254,3) and mask.shape==(1254,1254)
    a[T:B,L:R][mask]=raw[mask];combined[T:B,L:R]|=mask
    records.append({**item,'derivedSHA256':p.sha(item['derivedFile']),'supportSHA256':p.sha(item['supportFile']),'manifestSHA256':p.sha(item['manifest'])})
assert np.array_equal(a[~combined],original[~combined])
composite=p.save_png(out/'integrated-candidate-native.png',Image.fromarray(a))
support=p.save_png(out/'combined-support.png',Image.fromarray(combined.astype('uint8')*255))
exports=[];sel=p.read(p.ROOT/tile/'pipeline-selection.json')
for patch,old in sel.items():
    co=p.coords(tile,patch);w=co['worldBoxWithHalo'];tb=co['tileWorldBox'];L,T=w[0]-tb[0],w[1]-tb[1]
    x0,y0,x1,y1=max(L,0),max(T,0),min(L+1254,4096),min(T+1254,4096)
    m=combined[y0:y1,x0:x1]
    if not m.any():continue
    old=p.selected(p.ROOT/tile,patch);oldinfo=p.native_info(old);b=np.array(Image.open(old).convert('RGB'));before=b.copy()
    b[y0-T:y1-T,x0-L:x1-L][m]=a[y0:y1,x0:x1][m]
    fullmask=np.zeros((1254,1254),bool);fullmask[y0-T:y1-T,x0-L:x1-L]=m
    assert np.array_equal(b[~fullmask],before[~fullmask])
    file=out/(patch+'-derived.png');info=p.save_png(file,Image.fromarray(b))
    maskinfo=p.save_png(out/(patch+'-source-mask.png'),Image.fromarray(fullmask.astype('uint8')*255))
    sidecar={'schemaVersion':1,'kind':'native_multi_source_context_derivation','nativeToolOutput':False,'tile':tile,'patch':patch,**info,'width':1254,'height':1254,'format':'PNG','opaque':True,'resizedAfterGeneration':False,'finalArtUpscaled':False,'actualModel':None,'actualQuality':None,'baseNative':oldinfo,'coordinates':co,'repairContexts':records,'sourceMask':maskinfo,'operation':'Copy final already-composited pixels where support mask is positive, at the identical world coordinate. No additional alpha, resize, warp, or blur. Other native patch pixels unchanged.','copiedPixels':int(fullmask.sum()),'changedPixels':int(np.any(b!=before,axis=2).sum()),'verifiedOutsideRepairMaskUnchanged':True,'formalAccepted':False}
    p.put_json(Path(str(file)+'.generation.json'),sidecar);exports.append({'patch':patch,'file':str(file),'relativePath':str(file.relative_to(p.ROOT/tile)),**info})
manifest={'tile':tile,'baseCandidate':{'file':str(base),'sha256':p.sha(base)},'baseSelection':sel,'contextsInApplicationOrder':records,'integratedComposite':composite,'combinedSupport':support,'exports':exports,'verifiedOutsideSupportUnchanged':True,'external4096EdgesUnchanged':bool(not(combined[0].any() or combined[-1].any() or combined[:,0].any() or combined[:,-1].any())),'finalArtUpscaled':False,'formalAccepted':False}
p.put_json(out/'integration-manifest.json',manifest)
print(json.dumps({'manifest':str(out/'integration-manifest.json'),'candidate':composite,'exports':[{'patch':x['patch'],'relativePath':x['relativePath']} for x in exports]}))
