from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;R=T/'repairs-20261013';Q=T/'review/material-band-v2';Q.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ev(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def png(p,a):
 if Path(p).exists():assert np.array_equal(np.asarray(Image.open(p)),a)
 else:Image.fromarray(a).save(p)
 e=ev(p);e['size']=list(Image.open(p).size);return e
prep=read(R/'material-band-v1.preparation.json');base=np.asarray(Image.open(prep['baseCandidate']['path']).convert('RGB'));context=np.asarray(Image.open(prep['baseContext']['path']).convert('RGB')).copy()
receipt=read(R/'material-band-v1.tool-receipt.json');srcpath=R/'material-band-v1-native.png';src=np.asarray(Image.open(srcpath).convert('RGB'))
assert src.shape==(1254,1254,3)
assert ev(srcpath)['sha256']==ev(receipt['originalOutputPath'])['sha256']
assert np.array_equal(base[850:2104,2842:4096],np.asarray(Image.open(prep['target']['path'])))
req=read(R/'material-band-v1.request.json')
record={'schemaVersion':1,'tile':'r16_c14','id':'material-band-v1','file':str(srcpath),'sha256':ev(srcpath)['sha256'],'width':1254,'height':1254,'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'generatedAt':receipt['generatedAt'],'timestampBasis':receipt['timestampBasis'],'original':ev(receipt['originalOutputPath']),'receipt':ev(R/'material-band-v1.tool-receipt.json'),'request':ev(R/'material-band-v1.request.json'),'prompt':ev(R/'material-band-v1.prompt.txt'),'references':[ev(p) for p in req['referenced_image_paths']],'targetDerivation':{'source':prep['baseCandidate'],'cropBox':[2842,850,4096,2104],'resized':False},'resizedAfterGeneration':False,'status':'saved_local_repair_pending_composite_QA'}
save(R/'material-band-v1-native.png.generation.json',record)
yy,xx=np.mgrid[0:1254,0:1254]
mask=np.rint(np.minimum.reduce([np.clip((xx-180)/48,0,1),np.clip((yy-205)/32,0,1),np.clip((425-yy)/40,0,1)])*255).astype(np.uint8)
# Native right edge remains fully selected; no correction to source RGB.
maskinfo=png(R/'material-band-v2-alpha.png',mask);w=mask.astype(np.uint32)[...,None]
old=base[850:2104,2842:4096];out=base.copy();out[850:2104,2842:4096]=((old.astype(np.uint32)*(255-w)+src.astype(np.uint32)*w+127)//255).astype(np.uint8)
allowed=np.zeros((4096,4096),bool);allowed[850:2104,2842:4096]=mask>0
assert np.array_equal(out[~allowed],base[~allowed])
context[115:4211,115:4211]=out
candidate=png(T/'candidate/r16_c14-4k-material-repair-v2-20261013.png',out);ctx=png(T/'candidate/r16_c14-context-4326-material-repair-v2-20261013.png',context)
reviews=[]
for label,box in [('repair-full',[2842,850,4096,1500]),('repair-left-entry',[2980,1020,3420,1330]),('repair-mortar-crossing',[3460,1000,3820,1340]),('repair-east-edge',[3796,1000,4096,1340])]:
 x0,y0,x1,y1=box
 for version,a in [('before',base),('after',out)]:
  e=png(Q/f'{label}-{version}-100pct.png',a[y0:y1,x0:x1]);e.update(cropBox=box,resized=False);reviews.append(e)
m={'schemaVersion':1,'tile':'r16_c14','createdAt':datetime.now(timezone.utc).isoformat(),'status':'pending_local_visual_QA','baseManifest':prep['baseManifest'],'baseCandidate':prep['baseCandidate'],'baseContext':prep['baseContext'],'candidate':candidate,'context':ctx,'repairNative':ev(srcpath),'repairGenerationRecord':ev(R/'material-band-v1-native.png.generation.json'),'alpha':maskinfo,'placementInCore':[2842,850,4096,2104],'sourceCrop':[0,0,1254,1254],'blendArithmetic':'(base*(255-alpha)+source*alpha+127)//255, uint32','sourceResampling':False,'programmaticRgbCorrection':False,'appliedRepairSourceCount':1,'actualNativeOutputCount':18,'replay':{'baseSixteenNativesAndSavedAlpha':'verified in native49 index','repairPixelIdentical':True,'outsideSupportPixelIdentical':True,'northWestSouthEdgesPixelIdentical':True,'changedPixelCount':int(np.any(out!=base,axis=2).sum())},'reviewImages':reviews,'formalAccepted':False,'script':ev(__file__)}
save(T/'candidate/r16_c14-material-repair-v2-20261013-manifest.json',m)
print(json.dumps({'candidate':candidate,'context':ctx,'manifest':ev(T/'candidate/r16_c14-material-repair-v2-20261013-manifest.json'),'repair':ev(srcpath),'qaDirectory':str(Q),'changedPixels':m['replay']['changedPixelCount']},indent=2))
