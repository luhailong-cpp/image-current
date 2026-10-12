from datetime import datetime, timezone
import hashlib,json
from pathlib import Path
from PIL import Image
import numpy as np

D=Path(__file__).resolve().parent
S='r12c08-wall-rock-conditioned-v3'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
request=json.loads((D/(S+'.request.json')).read_text(encoding='utf-8-sig'))
rawpath=D/(S+'-raw.png'); guidepath=D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png'
nativepath=D/'r12c08-wall-rock-conditioned-v2-p14-provisional-native1254.png'
raw=Image.open(rawpath).convert('RGB'); base=Image.open(guidepath).convert('RGB')
assert raw.size==base.size==(1254,1254)
rect=[350,280,618,830]
adopt=base.copy(); adopt.paste(raw.crop(rect),rect[:2])
adoptpath=D/(S+'-bounded-adoption-preview.png'); assert not adoptpath.exists(); adopt.save(adoptpath)
native=Image.open(nativepath).convert('RGB'); native.paste(raw.crop(rect),(871,589))
nativeout=D/(S+'-p14-bounded-candidate-native1254.png'); assert not nativeout.exists(); native.save(nativeout)
aa=np.asarray(base); bb=np.asarray(raw); cc=np.asarray(adopt)
outside=np.ones((1254,1254),dtype=bool); outside[280:830,350:618]=False
stats={'rawOutsidePixelsChanged':int(np.any(aa!=bb,axis=2)[outside].sum()),
       'rawOutsidePixelCount':int(outside.sum()),
       'boundedOutsidePixelsChanged':int(np.any(aa!=cc,axis=2)[outside].sum()),
       'rawProtectedRailPixelsChanged':int(np.any(aa[0:241,320:650]!=bb[0:241,320:650],axis=2).sum())}
evidence=[]
boxes={'left':[286,280,414,830],'top':[350,216,618,344],
       'right':[554,280,682,830],'bottom':[350,766,618,894],
       'G4':[350,280,850,830],'G5':[430,670,760,960],'cross':[350,550,850,1050]}
for name,box in boxes.items():
    for phase,im in [('before',base),('raw',raw),('adopted',adopt)]:
        path=D/(S+'-'+name+'-'+phase+'-native.png'); assert not path.exists(); im.crop(box).save(path)
        evidence.append({'name':name,'phase':phase,'file':str(path),'sha256':sha(path),'guideBox':box,'dimensions':list(im.crop(box).size),'resampled':False})
receipt={'schemaVersion':1,'savedAtUtc':datetime.now(timezone.utc).isoformat(),
         'submittedAtUtc':'2026-10-12T12:28:57.015Z','completedAtUtc':'2026-10-12T12:29:25.139Z',
         'tool':'builtin image_gen.imagegen','status':'returned_image_success','paidApiUsed':False,
         'request':str(D/(S+'.request.json')),'requestSha256':sha(D/(S+'.request.json')),
         'actualToolInput':request['toolInput'],'actualReferences':[{'file':p,'sha256':sha(p)} for p in request['toolInput']['referenced_image_paths']],
         'originalBuiltinOutput':'C:/Users/luyua/.codex/generated_images/01a13003-bb39-7e00-ae6d-ced8fbe4df6b/exec-692c1ab6-dfd2-45f0-8d65-af134cc8eba3.png',
         'savedOutput':str(rawpath),'savedOutputSha256':sha(rawpath),'dimensions':list(raw.size),'opaque':True,
         'modelRequested':None,'qualityRequested':None,'actualModel':None,'actualQuality':None,
         'canonicalSelectionsModified':False,'formalAccepted':False,'acceptedForAdoption':None}
write(D/(S+'.generation-receipt.json'),receipt)
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'pending_native_visual_review','raw':str(rawpath),'rawSha256':sha(rawpath),
        'mechanicalAdoptionRectGuide':rect,'mechanicalAdoptionRectNativeP14':[871,589,1139,1139],
        'adoptionPreview':str(adoptpath),'adoptionSha256':sha(adoptpath),
        'candidate':str(nativeout),'candidateSha256':sha(nativeout),
        'operation':'Exact generated crop paste only; no resampling, synthesis, blend or feather.',
        'pixelEvidence':stats,'evidence':evidence,'formalAccepted':False,'selected':False}
write(D/(S+'.adoption-check.json'),report)
print(json.dumps({'receipt':str(D/(S+'.generation-receipt.json')),'report':str(D/(S+'.adoption-check.json')),'pixelEvidence':stats}))
