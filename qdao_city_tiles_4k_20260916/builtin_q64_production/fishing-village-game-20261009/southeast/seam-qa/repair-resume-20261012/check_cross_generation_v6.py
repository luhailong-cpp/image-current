from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;BASE=D.parent.parent
S='r12c08-wall-rock-conditioned-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
req=json.loads((D/(S+'.request.json')).read_text(encoding='utf-8-sig'))
rawpath=D/(S+'-raw.png');basepath=D/'r12c08-wall-rock-conditioned-v2-guide-native1254.png'
raw=Image.open(rawpath).convert('RGB');base=Image.open(basepath).convert('RGB');assert raw.size==base.size==(1254,1254)
rect=[350,280,950,830];world=[32500,45530,33100,46080];frame=[32150,45250,33404,46504]
adopt=base.copy();adopt.paste(raw.crop(rect),rect[:2]);adoptpath=D/(S+'-cross-bounded-preview.png');assert not adoptpath.exists();adopt.save(adoptpath)
outside=np.ones((1254,1254),bool);outside[280:830,350:950]=False
a=np.asarray(base);b=np.asarray(raw);c=np.asarray(adopt)
stats={'rawOutsidePixelsChanged':int(np.any(a!=b,axis=2)[outside].sum()),'rawOutsidePixelCount':int(outside.sum()),
       'boundedOutsidePixelsChanged':int(np.any(a!=c,axis=2)[outside].sum()),
       'protectedApprovedRailPixelsChanged':int(np.any(a[0:241,320:650]!=c[0:241,320:650],axis=2).sum())}
spec=importlib.util.spec_from_file_location('native_helper',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sources=helper.Sources();sources.tile('r12_c08')['selection']['patches']['p14']=str(D/'r12c08-wall-rock-conditioned-v2-p14-provisional-native1254.png')
patches=[]
for tile,pid in [('r12_c08','p14'),('r12_c08','p24'),('r12_c09','p11'),('r12_c09','p21')]:
    source,error=sources.source(tile,pid);assert not error,error
    nb=source['nativeBoxGlobal'];cb=source['coreBoxGlobal']
    inter=[max(world[0],nb[0]),max(world[1],nb[1]),min(world[2],nb[2]),min(world[3],nb[3])]
    coreinter=[max(world[0],cb[0]),max(world[1],cb[1]),min(world[2],cb[2]),min(world[3],cb[3])]
    im=Image.open(source['file']).convert('RGB');before=np.asarray(im).copy()
    crop=[inter[0]-frame[0],inter[1]-frame[1],inter[2]-frame[0],inter[3]-frame[1]]
    dest=[inter[0]-nb[0],inter[1]-nb[1]]
    im.paste(raw.crop(crop),dest)
    path=D/(S+'-'+tile+'-'+pid+'-provisional-native1254.png');assert not path.exists();im.save(path)
    unchanged=np.ones((1254,1254),bool);unchanged[dest[1]:dest[1]+inter[3]-inter[1],dest[0]:dest[0]+inter[2]-inter[0]]=False
    assert np.array_equal(before[unchanged],np.asarray(im)[unchanged])
    patches.append({'tile':tile,'patch':pid,'file':str(path),'sha256':sha(path),'source':source,
                    'nativeFrameWorld':nb,'worldAdoptionIntersection':inter,'generatedCrop':crop,'destinationNative':dest,
                    'coreAdoptionIntersection':coreinter if coreinter[0]<coreinter[2] and coreinter[1]<coreinter[3] else None,
                    'outsideAdoptionPixelReplayExact':True,'formalAccepted':False,'selected':False})
evidence=[]
boxes={'left':[286,280,414,830],'top':[350,216,950,344],'right':[886,280,1014,830],
       'bottom':[350,766,950,894],'G4':[350,280,950,830],'G5':[430,670,950,960],'cross':[350,550,950,1050]}
for name,box in boxes.items():
    for phase,im in [('before',base),('raw',raw),('adopted',adopt)]:
        p=D/(S+'-'+name+'-'+phase+'-native.png');assert not p.exists();im.crop(box).save(p)
        evidence.append({'name':name,'phase':phase,'file':str(p),'sha256':sha(p),'guideBox':box,'dimensions':list(im.crop(box).size),'resampled':False})
receipt={'schemaVersion':1,'savedAtUtc':datetime.now(timezone.utc).isoformat(),
         'tool':'builtin image_gen.imagegen','status':'returned_image_success','paidApiUsed':False,
         'request':str(D/(S+'.request.json')),'requestSha256':sha(D/(S+'.request.json')),
         'actualToolInput':req['toolInput'],'actualReferences':[{'file':p,'sha256':sha(p)} for p in req['toolInput']['referenced_image_paths']],
         'originalBuiltinOutput':'C:/Users/luyua/.codex/generated_images/01a13003-bb39-7e00-ae6d-ced8fbe4df6b/exec-af3f04fb-70cd-4cae-91aa-7c1a9a6eee47.png',
         'savedOutput':str(rawpath),'savedOutputSha256':sha(rawpath),'dimensions':[1254,1254],'opaque':True,
         'modelRequested':None,'qualityRequested':None,'actualModel':None,'actualQuality':None,
         'canonicalSelectionsModified':False,'formalAccepted':False,'acceptedForAdoption':None}
write(D/(S+'.generation-receipt.json'),receipt)
report={'schemaVersion':1,'status':'pending_native_visual_review','worldAdoptionBox':world,'guideAdoptionBox':rect,
        'guidePreview':str(adoptpath),'guidePreviewSha256':sha(adoptpath),'raw':str(rawpath),'rawSha256':sha(rawpath),
        'operation':'Exact native generated crop paste into source patches; no resize, warping, synthesis, blending or feathering.',
        'coreChanges':['r12_c08/p14','r12_c09/p11'],'haloOnlyChanges':['r12_c08/p24','r12_c09/p21'],
        'pixelEvidence':stats,'patches':patches,'evidence':evidence,'formalAccepted':False,'selected':False}
write(D/(S+'.cross-adoption-check.json'),report)
print(json.dumps({'report':str(D/(S+'.cross-adoption-check.json')),'receipt':str(D/(S+'.generation-receipt.json')),'pixelEvidence':stats}))
