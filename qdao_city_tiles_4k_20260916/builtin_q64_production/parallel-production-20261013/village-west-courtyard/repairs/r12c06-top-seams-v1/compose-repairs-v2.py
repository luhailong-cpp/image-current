from pathlib import Path
import json, hashlib, datetime
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent.parent
BASE = BATCH / 'qa/r12-c06-complete-native-v1/context-native.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write_json(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def save_image(path, array):
    assert not path.exists(), path
    Image.fromarray(array).save(path)
    return {'path':str(path.relative_to(HERE)), 'sha256':sha(path),
            'dimensions':list(Image.open(path).size)}

def dp_path(cost):
    # One native coordinate per row. Stable tie order: straight, -1, +1.
    rows, cols = cost.shape
    prev = cost[0].copy()
    links = np.zeros((rows, cols), dtype=np.int8)
    for row in range(1, rows):
        cand = np.stack((prev, np.r_[np.inf, prev[:-1]], np.r_[prev[1:], np.inf]))
        choice = np.argmin(cand, axis=0)
        links[row] = np.array([0,-1,1],np.int8)[choice]
        prev = cost[row] + np.min(cand, axis=0)
    path = np.empty(rows, dtype=np.int32)
    path[-1] = int(np.argmin(prev))
    for row in range(rows-1, 0, -1):
        path[row-1] = path[row] + links[row,path[row]]
    return path

base = np.array(Image.open(BASE).convert('RGB'))
candidate = base.copy()
source = np.zeros(base.shape[:2], dtype=np.uint8)
records = []
patches = {}
for source_id, name, band in [(1,'w01-I01-I03',80),(2,'w02-I02-I04',60)]:
    req_path = HERE / (name+'.request-v1.json')
    req = json.loads(req_path.read_text(encoding='utf-8'))
    image_path = HERE / (name+'.generated-v1.png')
    patch = np.array(Image.open(image_path).convert('RGB'))
    assert patch.shape == (1254,1254,3)
    x0,y0,x1,y1 = req['contextNativeBox']
    original = base[y0:y1,x0:x1]
    assert np.array_equal(original,np.array(Image.open(req['input']['path']).convert('RGB')))
    ax0,ay0,ax1,ay1 = req['allowedRepairLocalBox']
    if source_id == 2:
        ax0,ay0,ax1,ay1 = [115,115,650,525]
        req['allowedRepairLocalBox'] = [ax0,ay0,ax1,ay1]
        req['allowedRepairContextBox'] = [x0+ax0,y0+ay0,x0+ax1,y0+ay1]
        req['issues'] = ['I02']
    assert ax0>=115 and ay0>=115 and ax1<=1139 and ay1<=1139
    assert ax1-ax0<=1024 and ay1-ay0<=1024
    cost = np.mean((patch.astype(np.float64)-original.astype(np.float64))**2,axis=2)
    cost = cost[ay0:ay1,ax0:ax1]
    h,w = cost.shape
    left = dp_path(cost[:,:band])
    right = w-band+dp_path(cost[:,-band:])
    top = dp_path(cost[:band,:].T)
    bottom = h-band+dp_path(cost[-band:,:].T)
    yy,xx = np.indices((h,w))
    inside = (xx>=left[:,None]) & (xx<=right[:,None]) & (yy>=top[None,:]) & (yy<=bottom[None,:])
    mask = np.zeros((1254,1254),dtype=bool)
    mask[ay0:ay1,ax0:ax1] = inside
    assert not np.any(source[y0:y1,x0:x1][mask])
    candidate[y0:y1,x0:x1][mask] = patch[mask]
    source[y0:y1,x0:x1][mask] = source_id
    composite = original.copy(); composite[mask] = patch[mask]
    composite_record = save_image(HERE/(name+'.composite-native-v2.png'),composite)
    mask_record = save_image(HERE/(name+'.source-mask-v2.png'),mask.astype(np.uint8)*255)
    border = np.zeros((1254,1254),bool);border[:115]=True;border[-115:]=True;border[:,:115]=True;border[:,-115:]=True
    outside = np.ones((1254,1254),bool);outside[ay0:ay1,ax0:ax1]=False
    raw_diff = np.abs(patch.astype(float)-original.astype(float))
    patch_records=[]
    for side, box in [('top',[max(0,ax0-80),max(0,ay0-80),min(1254,ax1+80),min(1254,ay0+band+80)]),
                      ('bottom',[max(0,ax0-80),max(0,ay1-band-80),min(1254,ax1+80),min(1254,ay1+80)]),
                      ('left',[max(0,ax0-80),max(0,ay0-80),min(1254,ax0+band+80),min(1254,ay1+80)]),
                      ('right',[max(0,ax1-band-80),max(0,ay0-80),min(1254,ax1+80),min(1254,ay1+80)])]:
        l,t,r,b=box
        info=save_image(HERE/(name+'.border-'+side+'-native-v2.png'),composite[t:b,l:r])
        info.update({'sourceCompositeBox':box,'scale':1,'operation':'integer crop only','visualStatus':'pending'})
        patch_records.append(info)
    records.append({'sourceId':source_id,'id':name,'issues':req['issues'],'native':{'path':image_path.name,'sha256':sha(image_path),'dimensions':[1254,1254]},
        'request':{'path':req_path.name,'sha256':sha(req_path)},'contextNativeBox':req['contextNativeBox'],'globalNativeBox':req['globalNativeBox'],
        'allowedRepairContextBox':req['allowedRepairContextBox'],'allowedRepairLocalBox':req['allowedRepairLocalBox'],'dpBandWidth':band,
        'pathsInAllowedRectangle':{'left':left.tolist(),'right':right.tolist(),'top':top.tolist(),'bottom':bottom.tolist()},
        'sourceMask':mask_record,'composite':composite_record,'nativeBorderQa':patch_records,'selectedPixels':int(mask.sum()),
        'rawGeneratedOutsideAllowedRgbMae':float(raw_diff[outside].mean()),'rawGeneratedOuter115RgbMae':float(raw_diff[border].mean()),
        'compositeOutsideAllowedChangedPixels':int(np.any(composite[outside]!=original[outside],axis=1).sum()),
        'compositeOuter115ChangedPixels':int(np.any(composite[border]!=original[border],axis=1).sum()),'visualStatus':'pending'})
    patches[source_id]=(patch,(x0,y0,x1,y1))

context_record=save_image(HERE/'context-repair-candidate-v2.png',candidate)
tile_record=save_image(HERE/'r12_c06.repair-candidate-v2.png',candidate[115:4211,115:4211])
source_record=save_image(HERE/'repair-source-id-v2.png',source)
replay=base.copy()
for source_id,(patch,(x0,y0,x1,y1)) in patches.items():
    mask=source[y0:y1,x0:x1]==source_id
    replay[y0:y1,x0:x1][mask]=patch[mask]
outside=source==0
proof={'mismatchedReplayPixels':int(np.any(replay!=candidate,axis=2).sum()),
       'uncoveredPixels':0,'changedPixelsOutsideSelection':int(np.any(candidate[outside]!=base[outside],axis=1).sum()),
       'northHaloChangedPixels':int(np.any(candidate[:115]!=base[:115],axis=2).sum()),
       'northCoreFirstRowChangedPixels':int(np.any(candidate[115]!=base[115],axis=1).sum()),
       'selectedNewPixels':int(np.count_nonzero(source)), 'sourcePixelCounts':{str(i):int((source==i).sum()) for i in range(3)}}
trace={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'native-repair-candidate-pending-visual-QA',
       'formalAccepted':False,'tile':'r12_c06','scopeIssues':['I01','I02','I03'],'remainingIssuesNotResolved':['I04','I05','I06','I07','I08','I09','I10','I11','I12','I13','I14','north external seam'],
       'baseContext':{'path':str(BASE),'sha256':sha(BASE),'globalContextBox':[20365,44941,24691,49267],
       'upstreamAssembly':{'path':str(BASE.parent/'assembly.json'),'sha256':sha(BASE.parent/'assembly.json')},'sourceId':0},
       'contextCandidate':context_record,'tileCandidate':tile_record,'sourceIdMap':source_record,'patches':records,'proof':proof,
       'composition':{'method':'four constrained minimum squared RGB error paths enclosing each local repair; binary hard source selection',
        'maxPathStep':1,'resample':False,'blend':False,'feather':False,'rgbTransformation':False,'sourceIdMapAuthoritative':True},
       'actualGenerationModel':None,'route':'builtin-image_gen','script':{'path':Path(__file__).name,'sha256':sha(Path(__file__))}}
write_json(HERE/'repair-assembly-trace-v2.json',trace)
print(json.dumps({'proof':proof,'trace':'repair-assembly-trace-v2.json','context':context_record},ensure_ascii=False))
