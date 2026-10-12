from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).parent
ROOT=D.parents[1]
context=ROOT/'resume-20261012/prepared-contexts/rail-facet/context-native.png'
baseCandidate=ROOT/'r04_c04/candidate/r04_c04-pipeline-fixed-native-contexts-71cabb17b21f.png'
raw=D/'raw-native-v1.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=np.array(Image.open(context).convert('RGB'));new=np.array(Image.open(raw).convert('RGB'))
assert base.shape==new.shape==(1254,1254,3)
full=np.array(Image.open(baseCandidate).convert('RGB'));assert np.array_equal(base,full[2400:3654,300:1554])
box=[605,557,653,590];l,t,r,b=box
yy,xx=np.indices((1254,1254))
# Exact assigned half-open ROI; a3px transition stays wholly inside it.
dist=np.minimum.reduce([xx-l+1,r-xx,yy-t+1,b-yy])
alpha=np.where((xx>=l)&(xx<r)&(yy>=t)&(yy<b),np.clip(dist/3,0,1),0)
alpha=np.rint(alpha*255).astype(np.uint8)
out=((base.astype(np.uint32)*(255-alpha[:,:,None])+new.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
support=alpha>0
assert np.array_equal(out[~support],base[~support])
for name,a in [('derived-context-native.png',out),('source-alpha-u8.png',alpha),('source-support.png',support.astype(np.uint8)*255)]:
 Image.fromarray(a).save(D/name)
for name,a in [('qa-before-native.png',base),('qa-after-native.png',out)]:
 Image.fromarray(a[475:675,525:725]).save(D/name)
Image.fromarray(out[505:645,565:685]).save(D/'qa-facet-close-native.png')
m={'recordType':'two_source_native_same_coordinate_material_repair','tile':'r04_c04','formalAccepted':False,'nativeToolOutput':False,'baseCandidate':{'file':str(baseCandidate),'sha256':sha(baseCandidate)},'baseContext':{'file':str(context),'sha256':sha(context),'tileBox':[300,2400,1554,3654]},'raw':{'file':str(raw),'sha256':sha(raw),'generationRecord':str(raw)+'.generation.json','pixels':[1254,1254],'actualModel':None},'derived':{'file':str(D/'derived-context-native.png'),'sha256':sha(D/'derived-context-native.png'),'pixels':[1254,1254],'tileBox':[300,2400,1554,3654]},'targetTileROI':[905,2957,953,2990],'supportContextROI':box,'supportTileROI':[905,2957,953,2990],'supportPixels':int(support.sum()),'changedPixels':int(np.any(out!=base,axis=2).sum()),'sourceSupport':{'file':str(D/'source-support.png'),'sha256':sha(D/'source-support.png')},'sourceAlpha':{'file':str(D/'source-alpha-u8.png'),'sha256':sha(D/'source-alpha-u8.png'),'denominator':255,'formula':'round(255*min(1,min(x-l+1,r-x,y-t+1,b-y)/3)) inside ROI; zero outside'},'blendFormula':'(baseRGB*(255-alpha)+rawRGB*alpha+127)//255','resampled':False,'resizedAfterGeneration':False,'finalArtUpscaled':False,'blended':True,'colorCorrected':False,'outsideSupportPixelExact':True,'baseContextPixelExactToCandidate':True,'QA':[{'file':str(D/n),'sha256':sha(D/n),'nativePixelScale':1,'actuallyViewed':False} for n in ['qa-before-native.png','qa-after-native.png','qa-facet-close-native.png']],'selectionChanged':False,'progressChanged':False,'historicalRecordsChanged':False}
(D/'derivation.json').write_text(json.dumps(m,indent=2))
rec={'recordType':m['recordType'],'nativeToolOutput':False,'actualModel':None,'width':1254,'height':1254,'sha256':m['derived']['sha256'],'file':m['derived']['file'],'worldBoxWithHalo':[12588,14688,13842,15942],'resizedAfterGeneration':False,'finalArtUpscaled':False,'resampled':False,'blended':True,'derivationManifest':str(D/'derivation.json'),'formalAccepted':False}
(D/'derived-context-native.png.generation.json').write_text(json.dumps(rec,indent=2))
assert np.array_equal(np.array(Image.open(D/'derived-context-native.png')),out)
print(json.dumps({'manifest':str(D/'derivation.json'),'supportPixels':m['supportPixels'],'changedPixels':m['changedPixels'],'outsideSupportPixelExact':True,'sha256':m['derived']['sha256']}))

