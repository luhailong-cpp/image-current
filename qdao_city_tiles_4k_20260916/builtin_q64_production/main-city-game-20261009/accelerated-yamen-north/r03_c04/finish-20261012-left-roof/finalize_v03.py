from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;V=O/'v03';E=O/'accepted-v03';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p,image=False):
 d={'file':str(p),'sha256':sha(p)}
 if image:
  im=Image.open(p);d.update(pixels=list(im.size),mode=im.mode)
 return d
def write(p,obj):
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
prep=json.loads((O/'v01/preparation.json').read_text())
base=Path(prep['base']['file']);assert sha(base)==prep['base']['sha256']
tile=np.array(Image.open(base).convert('RGB'));assert tile.shape==(4096,4096,3)
context=np.array(Image.open(O/'v01/context-native.png').convert('RGB'))
D=np.array(Image.open(V/'derived-context.png').convert('RGB'))
support=np.array(Image.open(V/'combined-support.png'))>0
a2=np.array(Image.open(O/'v02/alpha.png')).astype('uint32');a3=np.array(Image.open(V/'alpha.png')).astype('uint32')
r2=np.array(Image.open(O/'v02/raw-native.png').convert('RGB')).astype('uint32');r3=np.array(Image.open(V/'raw-native.png').convert('RGB')).astype('uint32')
step=((context.astype('uint32')*(255-a2[:,:,None])+r2*a2[:,:,None]+127)//255)
rebuild=((step*(255-a3[:,:,None])+r3*a3[:,:,None]+127)//255).astype('uint8')
assert np.array_equal(rebuild,D)
assert np.array_equal(context[~support],D[~support])
owned=np.zeros((1254,1254),dtype=bool);owned[515:725,130:490]=True;owned[515:725,450:825]=True
assert not np.any(support & ~owned)
x0,y0,x1,y1=prep['contextTileBox']
sub=tile[y0:y1,x0:x1].copy();assert np.array_equal(sub,context)
tile_out=tile.copy();crop=tile_out[y0:y1,x0:x1];crop[support]=D[support]
global_support=np.zeros((4096,4096),dtype=bool);global_support[y0:y1,x0:x1]=support
assert np.array_equal(tile[~global_support],tile_out[~global_support])
Image.fromarray(tile_out).save(E/'r03_c04-two-left-roof-rois-4096.png')
for name,box in [('both-rois',[513,948,1338,1278]),('roi1',[543,968,983,1258]),('roi2',[863,968,1318,1258])]:
 Image.fromarray(tile_out).crop(box).save(E/(name+'-after-native.png'))
 Image.fromarray(tile).crop(box).save(E/(name+'-before-native.png'))
for version in ['v01','v02','v03']:
 d=O/version
 result=info(d/'raw-native.png',True)
 assert result['pixels']==[1254,1254]
 write(d/'raw-native.png.generation.json',{'schemaVersion':1,'tool':'image_gen.imagegen','route':'builtin','image':result,'parameters':info(d/'parameters.json'),'prompt':info(d/'prompt.txt'),'receipt':info(d/'receipt.json'),'preparation':info(d/'preparation.json'),'referenceSources':json.loads((d/'preparation.json').read_text())['referenceSources'],'actualModel':None,'actualQuality':None,'actualSize':[1254,1254],'postGenerationResampled':False,'rawBytesPreserved':True,'selectedIntoFinal':version in ['v02','v03']})
verdicts=[{'id':'left-roof-junction1','tileBox':[583,1008,943,1218],'worldBox':[12871,9200,13231,9410],'status':'PASS_LOCAL','finding':'旧锯齿和小V形缺口消除；圆弧瓦口顺畅收进下方连续暗槽。'}, {'id':'left-roof-junction2','tileBox':[903,1008,1278,1218],'worldBox':[13191,9200,13566,9410],'status':'PASS_LOCAL','finding':'旧大三角露缝消除；短弧形搭接领口及两边瓦沟连续。'}]
qa={'reviewer':'boundary_audit','actuallyViewedAtOriginalScale':True,'scope':'Only two assigned ROIs and their compositing entry edges; not whole tile acceptance','roiVerdicts':verdicts,'independentReviewer':'seam_diagnosis','independentVerdict':'PASS_LOCAL_BOTH','independentFinding':'四张原尺寸图实际查看：两洞接入边缘未见新直线接界、重影或明显色阶；双曲线为正常搭接领口。','viewedFiles':[info(V/(n+'.png'),True) for n in ['all-derived-qa','joint1-derived-qa','joint2-derived-qa','derived-context']],'finalCompositeQAFiles':[info(E/(n+'-after-native.png'),True) for n in ['both-rois','roi1','roi2']]}
write(E/'visual-review.json',qa)
ys,xs=np.where(support);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
manifest={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'kind':'native_multi_source_alpha_derivation','tile':'r03_c04','status':'PASS_LOCAL_TWO_ASSIGNED_ROIS','formalAccepted':False,'baseTile':info(base,True),'baseContext':info(O/'v01/context-native.png',True),'contextTileBox':prep['contextTileBox'],'contextWorldBox':prep['contextWorldBox'],'nativePixels':[1254,1254],'positiveSupportContextBox':bbox,'positiveSupportTileBox':[bbox[0]+x0,bbox[1]+y0,bbox[2]+x0,bbox[3]+y0],'ownedTileROIs':[v['tileBox'] for v in verdicts],'rawSources':[info(O/'v02/raw-native.png',True),info(V/'raw-native.png',True)],'generationRecords':[info(O/'v02/raw-native.png.generation.json'),info(V/'raw-native.png.generation.json')],'derivedFile':str(V/'derived-context.png'),'derivedHash':sha(V/'derived-context.png'),'supportPositiveMaskFile':str(V/'combined-support.png'),'supportPositiveMaskHash':sha(V/'combined-support.png'),'alphaFiles':[info(O/'v02/alpha.png',True),info(V/'alpha.png',True)],'sourceWeightFile':info(V/'source-weights.npz'),'alphaScale':255,'weightFormula':['base=(1-a2)*(1-a3)','v02=a2*(1-a3)','v03=a3'],'rounding':'Two stages integer RGB: (B*(255-A)+R*A+127)//255; use alpha PNGs for exact byte reconstruction. Float effective weights are explanatory; direct one-step rounding may differ by 1.','operation':'At contextTileBox origin (453,493), copy already-composited derived-context RGB only where combined-support.png >0. Do not alpha-composite the derived pixels again. Do not replace the complete context rectangle.','spatialTransform':'Identity on all original pixels; no rotation, resize or warp','sourcePixelsAndAlphaVerified':True,'reconstructionByteExact':True,'outsideSupportByteIdentical':True,'supportWhollyInsideAssignedROIs':True,'sourceBaseUnmodified':sha(base)==prep['base']['sha256'],'changedPixels':int(np.any(tile_out!=tile,axis=2).sum()),'candidateForLocalQA':info(E/'r03_c04-two-left-roof-rois-4096.png',True),'visualReview':info(E/'visual-review.json'),'actualModel':None,'actualQuality':None,'toolRequests':3,'historicalFailedLeftNarrowSourcesUsed':False,'v01Rejected':info(O/'v01/visual-review.json'),'selectionOrProgressModified':False,'inFlightRequests':0,'unsavedSuccessfulOutputs':0}
write(E/'manifest.json',manifest)
write(O/'handoff.json',{'status':'COMPLETE_LOCAL_TWO_ROIS_PASS','manifest':str(E/'manifest.json'),'derived':manifest['derivedFile'],'support':manifest['supportPositiveMaskFile'],'contextTileBox':prep['contextTileBox'],'contextWorldBox':prep['contextWorldBox'],'baseSHA256':sha(base),'acceptedROIs':verdicts,'applyInstruction':manifest['operation'],'qa':str(E/'visual-review.json'),'candidateForQA':manifest['candidateForLocalQA'],'generationRequests':3,'actualModel':None,'actualQuality':None,'formalAccepted':False,'selectionOrProgressModified':False,'inFlightRequests':0,'unsavedSuccessfulOutputs':0})
print(json.dumps({'handoff':str(O/'handoff.json'),'manifest':str(E/'manifest.json'),'derivedSHA':manifest['derivedHash'],'supportSHA':manifest['supportPositiveMaskHash'],'candidate':manifest['candidateForLocalQA'],'changedPixels':manifest['changedPixels']},ensure_ascii=False,indent=2))
