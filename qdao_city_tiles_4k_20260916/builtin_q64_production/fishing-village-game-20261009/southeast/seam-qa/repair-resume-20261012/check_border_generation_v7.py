from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent;S='r12c08-wall-rock-conditioned-v7';PREV='r12c08-wall-rock-conditioned-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
prev=json.loads((D/(PREV+'.cross-adoption-check.json')).read_text(encoding='utf-8'))
req=json.loads((D/(S+'.request.json')).read_text(encoding='utf-8'))
rawpath=D/(S+'-raw.png');basepath=Path(prev['guidePreview'])
raw=Image.open(rawpath).convert('RGB');base=Image.open(basepath).convert('RGB');assert raw.size==base.size==(1254,1254)
ring=[[350,280,950,344],[350,766,950,830],[350,344,414,766],[886,344,950,766]]
worldring=[[x0+32150,y0+45250,x1+32150,y1+45250] for x0,y0,x1,y1 in ring]
adopt=base.copy()
for box in ring:adopt.paste(raw.crop(box),box[:2])
adoptpath=D/(S+'-border-bounded-preview.png');assert not adoptpath.exists();adopt.save(adoptpath)
mask=np.zeros((1254,1254),bool)
for x0,y0,x1,y1 in ring:mask[y0:y1,x0:x1]=True
a=np.asarray(base);b=np.asarray(adopt)
stats={'outsideRingPixelsChanged':int(np.any(a!=b,axis=2)[~mask].sum()),
       'protectedApprovedRailPixelsChanged':int(np.any(a[0:241,320:650]!=b[0:241,320:650],axis=2).sum()),
       'centerPixelsChanged':int(np.any(a[344:766,414:886]!=b[344:766,414:886],axis=2).sum())}
assert stats['outsideRingPixelsChanged']==stats['protectedApprovedRailPixelsChanged']==stats['centerPixelsChanged']==0
patches=[]
for rec in prev['patches']:
    tile,pid=rec['tile'],rec['patch'];nb=rec['nativeFrameWorld']
    im=Image.open(rec['file']).convert('RGB');before=np.asarray(im).copy();inside=np.zeros((1254,1254),bool);uses=[]
    for wbox in worldring:
        inter=[max(wbox[0],nb[0]),max(wbox[1],nb[1]),min(wbox[2],nb[2]),min(wbox[3],nb[3])]
        if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
        crop=[inter[0]-32150,inter[1]-45250,inter[2]-32150,inter[3]-45250];dest=[inter[0]-nb[0],inter[1]-nb[1]]
        im.paste(raw.crop(crop),dest);inside[dest[1]:dest[1]+inter[3]-inter[1],dest[0]:dest[0]+inter[2]-inter[0]]=True
        uses.append({'worldBox':inter,'generatedCrop':crop,'destinationNative':dest})
    assert np.array_equal(before[~inside],np.asarray(im)[~inside])
    path=D/(S+'-'+tile+'-'+pid+'-provisional-native1254.png');assert not path.exists();im.save(path)
    patches.append({'tile':tile,'patch':pid,'file':str(path),'sha256':sha(path),'source':rec['file'],'sourceSha256':sha(rec['file']),
                    'nativeFrameWorld':nb,'coreAdoptionIntersection':rec['coreAdoptionIntersection'],'borderAdoptions':uses,
                    'outsideBorderPixelReplayExact':True,'formalAccepted':False,'selected':False})
evidence=[]
boxes={'left':[286,280,414,830],'top':[350,216,950,344],'right':[886,280,1014,830],'bottom':[350,766,950,894],
       'inner-left':[382,344,446,766],'inner-top':[414,312,886,376],
       'inner-right':[854,344,918,766],'inner-bottom':[414,734,886,798],
       'G4':[350,280,950,830],'G5':[430,670,950,960],'cross':[350,550,950,1050]}
for name,box in boxes.items():
    p=D/(S+'-'+name+'-adopted-native.png');assert not p.exists();adopt.crop(box).save(p)
    evidence.append({'name':name,'file':str(p),'sha256':sha(p),'guideBox':box,'dimensions':list(adopt.crop(box).size),'resampled':False})
receipt={'schemaVersion':1,'savedAtUtc':datetime.now(timezone.utc).isoformat(),
         'tool':'builtin image_gen.imagegen','status':'returned_image_success','paidApiUsed':False,
         'request':str(D/(S+'.request.json')),'requestSha256':sha(D/(S+'.request.json')),
         'actualToolInput':req['toolInput'],'actualReferences':[{'file':p,'sha256':sha(p)} for p in req['toolInput']['referenced_image_paths']],
         'originalBuiltinOutput':'C:/Users/luyua/.codex/generated_images/01a13003-bb39-7e00-ae6d-ced8fbe4df6b/exec-5659eb4a-2791-41b8-9f6c-04d633326139.png',
         'savedOutput':str(rawpath),'savedOutputSha256':sha(rawpath),'dimensions':[1254,1254],'opaque':True,
         'modelRequested':None,'qualityRequested':None,'actualModel':None,'actualQuality':None,
         'canonicalSelectionsModified':False,'formalAccepted':False,'acceptedForAdoption':None}
write(D/(S+'.generation-receipt.json'),receipt)
report={'schemaVersion':1,'status':'pending_native_visual_review','worldAdoptionBox':prev['worldAdoptionBox'],
        'guideBorderStrips':ring,'worldBorderStrips':worldring,
        'guidePreview':str(adoptpath),'guidePreviewSha256':sha(adoptpath),'raw':str(rawpath),'rawSha256':sha(rawpath),
        'operation':'Exact native generated border crop paste only; center and original surroundings replayed unchanged, no resize/warp/blend/synthesis.',
        'coreChanges':prev['coreChanges'],'haloOnlyChanges':prev['haloOnlyChanges'],
        'pixelEvidence':stats,'patches':patches,'evidence':evidence,'formalAccepted':False,'selected':False}
write(D/(S+'.border-adoption-check.json'),report)
print(json.dumps({'report':str(D/(S+'.border-adoption-check.json')),'pixelEvidence':stats}))
