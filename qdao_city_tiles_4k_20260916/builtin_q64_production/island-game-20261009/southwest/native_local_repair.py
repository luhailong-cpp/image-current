"""Select a same-coordinate native AI repair with four continuous hard cut paths.

Only writes qa/hardseam-* files. Never blends, shifts, recolors, or resamples art.
The central patch rectangle, inset by at most 150 pixels, must use the AI repair.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
QA = ROOT/'qa'
PARAMS = {'rgbDifferenceWeight':1.0, 'gradientDifferenceWeight':0.4,
          'gradientStrengthWeight':0.08, 'lateralStepPenalty':0.75,
          'centerBiasPerPixel':0.0002, 'maxStepPerPixel':1, 'edgeMarginPixels':3}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def dump(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def cost_path(old, new, side):
    a, b = old.astype(np.float32), new.astype(np.float32)
    diff = np.abs(a-b).mean(2)
    ay, ax = np.gradient(a, axis=(0,1))
    by, bx = np.gradient(b, axis=(0,1))
    gd = (np.abs(ax-bx)+np.abs(ay-by)).mean(2)
    gs = np.maximum(np.hypot(ax,ay).mean(2), np.hypot(bx,by).mean(2))
    h,w = diff.shape
    cost = diff+PARAMS['gradientDifferenceWeight']*gd+PARAMS['gradientStrengthWeight']*gs
    cost += np.abs(np.arange(w)-w//2)[None,:]*PARAMS['centerBiasPerPixel']
    margin = PARAMS['edgeMarginPixels']
    cost[:,:margin] = np.inf
    cost[:,-margin:] = np.inf
    prev = cost[0].copy()
    back = np.zeros((h,w),np.int8)
    for y in range(1,h):
        steps = np.stack((np.r_[np.inf,prev[:-1]+PARAMS['lateralStepPenalty']], prev,
                          np.r_[prev[1:]+PARAMS['lateralStepPenalty'],np.inf]))
        choice = steps.argmin(0)
        back[y] = choice.astype(np.int8)-1
        prev = steps[choice,np.arange(w)]+cost[y]
    path = np.empty(h,np.int16)
    path[-1] = prev.argmin()
    for y in range(h-1,0,-1):
        path[y-1] = path[y]+back[y,path[y]]
    assert np.max(np.abs(np.diff(path)))<=1
    values = diff[np.arange(h),path]
    return path, {'side':side, 'path':path.tolist(), 'pathMin':int(path.min()), 'pathMax':int(path.max()),
                  'pathInterpretation':'Distance from this patch edge to first AI pixel; along rows for left/right and columns for top/bottom',
                  'rgbDifferenceMean':float(values.mean()), 'rgbDifferenceP95':float(np.percentile(values,95)),
                  'rgbDifferenceMax':float(values.max())}

def main(args):
    for prefix in (args.base_prefix,args.prefix):
        assert re.fullmatch(r'hardseam(?:-[a-zA-Z0-9]+)*',prefix)
    assert args.prefix != args.base_prefix
    assert re.fullmatch(r'[a-zA-Z0-9_]+',args.repair)
    assert 7<=args.band<=150 and 1<=args.source_id<=255
    basepath = QA/(args.base_prefix+'-candidate-4096.png')
    maskpath = QA/(args.base_prefix+'-source-id-mask.png')
    base_report_path = QA/(args.base_prefix+'-report.json')
    repairpath = ROOT/'native'/(args.repair+'.png')
    repair_record_path = Path(str(repairpath)+'.generation.json')
    base_report, repair_record = load(base_report_path), load(repair_record_path)
    base, ids, repair = np.array(Image.open(basepath)), np.array(Image.open(maskpath)), np.array(Image.open(repairpath))
    assert base.shape==(4096,4096,3) and ids.shape==(4096,4096) and repair.shape==(1254,1254,3)
    box = repair_record['coordinates']['tileLocalCrop']
    x0,y0,x1,y1 = box
    assert x1-x0==1254 and y1-y0==1254 and min(x0,y0)>=0 and max(x1,y1)<=4096
    global_box = [8192+x0,32768+y0,8192+x1,32768+y1]
    assert repair_record['coordinates']['nativeGlobalBox']==global_box
    assert sha(repairpath)==repair_record['sha256']
    assert args.source_id not in np.unique(ids)
    old = base[y0:y1,x0:x1]
    band = args.band
    rois = args.repair_roi or [[0,0,1254,1254]]
    selected = np.zeros((1254,1254),bool)
    records,cores = [],[]
    for roi_index,roi in enumerate(rois,1):
        rx0,ry0,rx1,ry1 = roi
        assert 0<=rx0<rx1<=1254 and 0<=ry0<ry1<=1254
        rh,rw = ry1-ry0,rx1-rx0
        assert min(rh,rw)>2*band
        old_roi,new_roi = old[ry0:ry1,rx0:rx1],repair[ry0:ry1,rx0:rx1]
        transforms = {
          'left':(old_roi[:,:band],new_roi[:,:band]),
          'right':(old_roi[:,::-1][:,:band],new_roi[:,::-1][:,:band]),
          'top':(old_roi[:band].transpose(1,0,2),new_roi[:band].transpose(1,0,2)),
          'bottom':(old_roi[::-1][:band].transpose(1,0,2),new_roi[::-1][:band].transpose(1,0,2))}
        paths = {}
        for side,(a,b) in transforms.items():
            paths[side],record = cost_path(a,b,side)
            record.update({'roiIndex':roi_index,'repairPatchRoi':roi})
            records.append(record)
        yy,xx = np.indices((rh,rw))
        roi_selected = ((xx>=paths['left'][:,None]) & (xx<rw-paths['right'][:,None]) &
                       (yy>=paths['top'][None,:]) & (yy<rh-paths['bottom'][None,:]))
        assert roi_selected[band:rh-band,band:rw-band].all()
        selected[ry0:ry1,rx0:rx1] |= roi_selected
        cores.append([rx0+band,ry0+band,rx1-band,ry1-band])
    targets = args.mandatory_target or []
    for tx0,ty0,tx1,ty1 in targets:
        assert 0<=tx0<tx1<=1254 and 0<=ty0<ty1<=1254
        assert selected[ty0:ty1,tx0:tx1].all(), 'Mandatory repair target must entirely use AI pixels'
    candidate = base.copy()
    candidate[y0:y1,x0:x1] = np.where(selected[...,None],repair,old)
    out_ids = ids.copy()
    out_ids[y0:y1,x0:x1][selected] = args.source_id
    global_selection = out_ids==args.source_id
    assert np.array_equal(candidate[~global_selection],base[~global_selection])
    inputs = base_report['inputs']+[{'sourceId':args.source_id, 'stem':args.repair,
          'path':repairpath.as_posix(),'sha256':sha(repairpath),'nativeGlobalBox':global_box,
          'record':repair_record_path.as_posix(),'recordSha256':sha(repair_record_path),
          'role':'native AI local tone repair; full mandatory central region selected'}]
    artifacts=[]
    def save(label,arr,meta=None):
        p = QA/(args.prefix+'-'+label+'.png')
        Image.fromarray(arr).save(p)
        rec = {'path':p.as_posix(),'dimensions':list(Image.open(p).size),'sha256':sha(p)}
        if meta:
            rec.update(meta)
        artifacts.append(rec)
        return p
    candidate_path = save('candidate-4096',candidate)
    id_path = save('source-id-mask',out_ids)
    save('repair-selection-mask',global_selection.astype(np.uint8)*255,{'binaryValues':[0,255]})
    save('repair-local-selection-mask',selected.astype(np.uint8)*255,{'binaryValues':[0,255],'tileLocalBox':box})
    save('preview-1254-QA-only',np.array(Image.fromarray(candidate).resize((1254,1254),Image.Resampling.LANCZOS)),{'resampledQAPreviewOnly':True})
    save('repair-area-base-left-candidate-right-100pct',np.concatenate((old,candidate[y0:y1,x0:x1]),axis=1),{'sourceCrop':box,'scale':'1:1'})
    for roi_index,roi in enumerate(rois,1):
        rx0,ry0,rx1,ry1 = roi
        ax0,ay0,ax1,ay1=x0+rx0,y0+ry0,x0+rx1,y0+ry1
        edge_boxes = {'top':[ax0,ay0-75,ax1,ay0+band+75], 'bottom':[ax0,ay1-band-75,ax1,ay1+75],
                      'left':[ax0-75,ay0,ax0+band+75,ay1], 'right':[ax1-band-75,ay0,ax1+75,ay1]}
        for side,crop in edge_boxes.items():
            cx0,cy0,cx1,cy1 = crop
            assert min(cx0,cy0)>=0 and max(cx1,cy1)<=4096
            a,b = base[cy0:cy1,cx0:cx1],candidate[cy0:cy1,cx0:cx1]
            label=('roi'+str(roi_index)+'-' if args.repair_roi else '')+'boundary-'+side+'-base-first-candidate-second-100pct'
            save(label,np.concatenate((a,b),axis=0 if side in ('top','bottom') else 1),{'sourceCrop':crop,'scale':'1:1'})
        for cy in (ay0,ay1):
            for cx in (ax0,ax1):
                crop=[cx-150,cy-150,cx+150,cy+150]
                a,b=base[cy-150:cy+150,cx-150:cx+150],candidate[cy-150:cy+150,cx-150:cx+150]
                save(f'corner-{cx}-{cy}-base-left-candidate-right-100pct',np.concatenate((a,b),axis=1),{'sourceCrop':crop,'scale':'1:1'})
    # Reopen the written PNG and mask, then validate against every recorded source.
    disk = np.array(Image.open(candidate_path))
    disk_ids = np.array(Image.open(id_path))
    counts={}
    validated=0
    for source in inputs:
        sid=source['sourceId']
        sy,sx = np.where(disk_ids==sid)
        source_image=np.array(Image.open(source['path']))
        nx=sx+8192-source['nativeGlobalBox'][0]
        ny=sy+32768-source['nativeGlobalBox'][1]
        assert len(sx)>0 and nx.min()>=0 and ny.min()>=0 and nx.max()<source_image.shape[1] and ny.max()<source_image.shape[0]
        assert np.array_equal(disk[sy,sx],source_image[ny,nx]),sid
        assert sha(source['path'])==source['sha256']
        counts[str(sid)]=len(sx)
        validated+=len(sx)
    assert validated==4096**2
    assert np.array_equal(disk,candidate) and np.array_equal(disk_ids,out_ids)
    assert np.array_equal(np.array(Image.open(QA/(args.prefix+'-repair-selection-mask.png')))>0,global_selection)
    validation={'pixelCount':validated,'mismatchedPixels':0,'sameGlobalCoordinateExact':True,
                'sourceIdPixelCounts':counts,'unchangedOutsideRepairSelection':True,'sourceInputsUnchanged':True,
                'mandatoryCorePatchBoxes':cores, 'mandatoryCoreUsesRepairOnly':True,
                'mandatoryTargetPatchBoxes':targets,'mandatoryTargetsUseRepairOnly':True,
                'diskRoundtripExact':True,'interpolation':False,'feathering':False,'colorAdjustment':False,'displacement':False}
    if args.repair=='r09_c03_tone_lower_cross_v01':
        assert selected[400:600,980:1050].all()
        validation['rightWallTargetPatchBox']=[980,400,1050,600]
        validation['rightWallTargetUsesRepairOnly']=True
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r09_c03','status':'candidate_pending_visual_QA; not formal',
            'algorithm':'Intersection of four continuous DP hard-cut paths, each confined to its edge band; all chosen pixels retain native global coordinates',
            'parameters':{**PARAMS,'bandPixels':band,'repairRois':rois},'paths':records,'inputs':inputs,'outputs':artifacts,
            'baseCandidate':{'path':basepath.as_posix(),'sha256':sha(basepath)},
            'baseSourceIdMask':{'path':maskpath.as_posix(),'sha256':sha(maskpath)},
            'baseReport':{'path':base_report_path.as_posix(),'sha256':sha(base_report_path)},
            'script':{'path':Path(__file__).as_posix(),'sha256':sha(__file__)},
            'repairTileLocalBox':box,'repairGlobalBox':global_box,'candidateGlobalBox':[8192,32768,12288,36864],
            'validation':validation,'limitations':['This operation selects pixels; any actual painting repair comes from the recorded native AI source.',
            'Continuous edge paths intersect at corners, and source lighting disagreement can remain visible.']}
    dump(QA/(args.prefix+'-report.json'),report)
    print(json.dumps({'candidate':candidate_path.as_posix(),'sha256':sha(candidate_path),'repairPixelCount':int(selected.sum()),'validation':validation}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-prefix',default='hardseam-v02')
    parser.add_argument('--prefix',default='hardseam-v03')
    parser.add_argument('--repair',default='r09_c03_tone_lower_cross_v01')
    parser.add_argument('--source-id',type=int,default=17)
    parser.add_argument('--band',type=int,default=150)
    parser.add_argument('--repair-roi',type=int,nargs=4,action='append',help='Repeat for separate native selection regions; coordinates within the original repair image')
    parser.add_argument('--mandatory-target',type=int,nargs=4,action='append',help='Force full target rectangle to be selected from AI within its ROI core')
    main(parser.parse_args())
