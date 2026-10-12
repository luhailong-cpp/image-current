"""Parameterised QA-only 4x4 native tile assembly.

All art pixels retain the selected source's exact global coordinates. Binary hard
cuts are confined to 230-pixel overlaps. No resampling, blending or recolouring is
used for candidate art. Only the explicitly labelled QA preview is downsampled.
Outputs are restricted to qa/c04-hardseam-*; inputs/index/progress are read-only.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
QA = ROOT/'qa'
STEP, NATIVE, HALO, OVERLAP, TILE_SIZE = 1024, 1254, 115, 230, 4096
PARAMS = {'rgbDifferenceWeight':1.0, 'gradientDifferenceWeight':0.4,
          'gradientStrengthWeight':0.08, 'lateralStepPenalty':0.75,
          'centerBiasPerPixel':0.0002, 'maxStepPerPixel':1, 'edgeMarginPixels':3}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def dump(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def inspect_sources(tile, index_path=None):
    """Return status/16 selected sources; report every absent slot without artwork."""
    match = re.fullmatch(r'r([0-9]{2})_c([0-9]{2})',tile)
    if not match or min(map(int,match.groups()))<1:
        raise ValueError('Tile must use positive one-based rNN_cNN coordinates.')
    index_path = Path(index_path or ROOT/'current-native-map.json')
    index = load(index_path)
    selected = index.get(tile)
    missing, entries = [],[]
    if selected is not None and (not isinstance(selected,list) or len(selected)!=4 or
                                any(not isinstance(row,list) or len(row)!=4 for row in selected)):
        raise ValueError(f'{tile}: selected source map must contain exactly four rows of four slots.')
    for r in range(4):
        for c in range(4):
            stem = selected[r][c] if selected is not None else None
            item = {'subrow':r+1,'subcolumn':c+1,'slot':f's{r+1:02}_{c+1:02}','source':stem}
            if not stem:
                missing.append({**item,'reason':'source_not_selected'})
                continue
            if not isinstance(stem,str) or not re.fullmatch(r'[A-Za-z0-9_]+',stem):
                raise ValueError(f'{tile} {item["slot"]}: unsafe or invalid native source stem.')
            path = ROOT/'native'/(stem+'.png')
            record_path = Path(str(path)+'.generation.json')
            absent = [p.as_posix() for p in (path,record_path) if not p.is_file()]
            if absent:
                missing.append({**item,'reason':'source_or_record_file_missing','absentPaths':absent})
                continue
            entries.append({**item,'sourceId':r*4+c+1,'path':path.as_posix(),'record':record_path.as_posix()})
    return {'tile':tile,'status':'waiting_for_sources' if missing else 'ready',
            'expectedSources':16,'availableSources':len(entries),'missing':missing,'entries':entries,
            'selectedArray':selected,'indexPath':index_path.as_posix(),'indexSha256':sha(index_path),
            'selectedBaseArrayOnly':True,
            'separateCandidateArtifact':index.get('candidateArtifacts',{}).get(tile),
            'note':'Only the 4x4 selected array is assembled. Separately indexed later local repairs are not included.'}

def read_sources(inventory):
    """Read coordinates from generation records; enforce a native 4x4 grid."""
    if inventory['missing']:
        raise ValueError('Cannot assemble while native sources are missing.')
    arrays, inputs = [],[]
    origin = None
    for entry in inventory['entries']:
        path, record_path = Path(entry['path']),Path(entry['record'])
        record = load(record_path)
        box = record.get('coordinates',{}).get('nativeGlobalBox')
        if not isinstance(box,list) or len(box)!=4 or not all(isinstance(v,int) for v in box):
            raise ValueError(f'{entry["source"]}: missing integer nativeGlobalBox.')
        if box[2]-box[0]!=NATIVE or box[3]-box[1]!=NATIVE:
            raise ValueError(f'{entry["source"]}: coordinate footprint is not 1254x1254.')
        r,c = entry['subrow']-1,entry['subcolumn']-1
        inferred_origin = [box[0]+HALO-c*STEP,box[1]+HALO-r*STEP]
        if origin is None:
            origin = inferred_origin
        if inferred_origin!=origin:
            raise ValueError(f'{entry["source"]}: source coordinates do not fit the 1024-pixel grid.')
        if record['coordinates'].get('tile',inventory['tile'])!=inventory['tile']:
            raise ValueError(f'{entry["source"]}: generation record belongs to another tile.')
        with Image.open(path) as im:
            if im.mode!='RGB' or im.size!=(NATIVE,NATIVE):
                raise ValueError(f'{entry["source"]}: expected native RGB 1254x1254, got {im.mode} {im.size}.')
            arrays.append(np.array(im))
        file_hash = sha(path)
        if record.get('sha256')!=file_hash:
            raise ValueError(f'{entry["source"]}: image does not match the generation record hash.')
        inputs.append({'sourceId':entry['sourceId'],'row':r+1,'column':c+1,'stem':entry['source'],
                       'path':path.as_posix(),'sha256':file_hash,'nativeGlobalBox':box,
                       'record':record_path.as_posix(),'recordSha256':sha(record_path)})
    row,col = map(int,re.fullmatch(r'r([0-9]{2})_c([0-9]{2})',inventory['tile']).groups())
    expected_origin = [(col-1)*TILE_SIZE,(row-1)*TILE_SIZE]
    if origin!=expected_origin:
        raise ValueError(f'Recorded tile origin {origin} conflicts with {inventory["tile"]} origin {expected_origin}.')
    return arrays,inputs,origin

def select_seam(a,b,label,params=None):
    """Return first-B-column for each scanline; adjacent steps are at most one."""
    params = params or PARAMS
    if a.shape!=b.shape or a.shape[1:]!=(OVERLAP,3):
        raise ValueError('Seam inputs must have matching Hx230x3 shapes.')
    af,bf = a.astype(np.float32),b.astype(np.float32)
    diff = np.abs(af-bf).mean(2)
    agy,agx = np.gradient(af,axis=(0,1))
    bgy,bgx = np.gradient(bf,axis=(0,1))
    gd = (np.abs(agx-bgx)+np.abs(agy-bgy)).mean(2)
    gs = np.maximum(np.hypot(agx,agy).mean(2),np.hypot(bgx,bgy).mean(2))
    cost = params['rgbDifferenceWeight']*diff+params['gradientDifferenceWeight']*gd+params['gradientStrengthWeight']*gs
    cost += np.abs(np.arange(OVERLAP)-HALO)[None,:]*params['centerBiasPerPixel']
    margin = params['edgeMarginPixels']
    cost[:,:margin] = np.inf
    cost[:,-margin:] = np.inf
    prev,back = cost[0].copy(),np.zeros(cost.shape,np.int8)
    for y in range(1,len(cost)):
        options = np.stack((np.r_[np.inf,prev[:-1]+params['lateralStepPenalty']],prev,
                            np.r_[prev[1:]+params['lateralStepPenalty'],np.inf]))
        choice = options.argmin(0)
        back[y] = choice.astype(np.int8)-1
        prev = options[choice,np.arange(OVERLAP)]+cost[y]
    path = np.empty(len(cost),np.int16)
    path[-1] = prev.argmin()
    for y in range(len(path)-1,0,-1):
        path[y-1] = path[y]+back[y,path[y]]
    assert np.max(np.abs(np.diff(path)))<=1
    def stats(values):
        return {'mean':float(values.mean()),'p95':float(np.percentile(values,95)),'max':float(values.max())}
    return path,{'label':label,'path':path.tolist(),'pathMin':int(path.min()),'pathMax':int(path.max()),
                'rgbDifferenceChosen':stats(diff[np.arange(len(path)),path]),
                'rgbDifferenceMidpoint':stats(diff[:,HALO])}

def join(a,aid,b,bid,offset,label,params=None):
    """Join aligned rectangles with a binary same-coordinate overlap selection."""
    assert offset+OVERLAP==a.shape[1] and a.shape[0]==b.shape[0]
    left,right = a[:,offset:offset+OVERLAP],b[:,:OVERLAP]
    path,record = select_seam(left,right,label,params)
    use_b = np.arange(OVERLAP)[None,:]>=path[:,None]
    out = np.empty((a.shape[0],offset+b.shape[1],3),np.uint8)
    ids = np.empty(out.shape[:2],np.uint8)
    out[:,:a.shape[1]],ids[:,:a.shape[1]] = a,aid
    out[:,offset+OVERLAP:],ids[:,offset+OVERLAP:] = b[:,OVERLAP:],bid[:,OVERLAP:]
    out[:,offset:offset+OVERLAP] = np.where(use_b[...,None],right,left)
    ids[:,offset:offset+OVERLAP] = np.where(use_b,bid[:,:OVERLAP],aid[:,offset:offset+OVERLAP])
    record['overlapOffset'] = offset
    return out,ids,record

def assemble(arrays,origin,params=None):
    """Assemble 16 row-major native arrays and return 4096 art, source IDs, trace."""
    if len(arrays)!=16:
        raise ValueError('Exactly 16 native sources are required.')
    rows,row_ids,seams = [],[],[]
    native_origin = [origin[0]-HALO,origin[1]-HALO]
    for r in range(4):
        canvas = arrays[r*4]
        ids = np.full((NATIVE,NATIVE),r*4+1,np.uint8)
        for c in range(1,4):
            canvas,ids,record = join(canvas,ids,arrays[r*4+c],np.full((NATIVE,NATIVE),r*4+c+1,np.uint8),c*STEP,f'row-{r+1}-columns-{c}-{c+1}',params)
            record.update({'orientation':'vertical; first-B-column-per-row',
                           'assemblyFrameOriginGlobal':[native_origin[0],native_origin[1]+r*STEP]})
            seams.append(record)
        rows.append(canvas)
        row_ids.append(ids)
    canvas,ids = rows[0],row_ids[0]
    for r in range(1,4):
        trans,tids,record = join(canvas.transpose(1,0,2),ids.T,rows[r].transpose(1,0,2),row_ids[r].T,r*STEP,f'rows-{r}-{r+1}',params)
        canvas,ids = trans.transpose(1,0,2),tids.T
        record.update({'orientation':'horizontal; first-B-row-per-column','assemblyFrameOriginGlobal':native_origin})
        seams.append(record)
    assert canvas.shape==(4326,4326,3)
    return canvas[HALO:HALO+TILE_SIZE,HALO:HALO+TILE_SIZE].copy(),ids[HALO:HALO+TILE_SIZE,HALO:HALO+TILE_SIZE].copy(),seams

def validate_pixels(candidate,ids,inputs,origin):
    """Reconstruct every output pixel from source IDs and recorded global boxes."""
    assert candidate.shape==(4096,4096,3) and ids.shape==(4096,4096)
    assert np.array_equal(np.unique(ids),np.arange(1,17))
    counts,total = {},0
    for source in inputs:
        yy,xx = np.where(ids==source['sourceId'])
        nx,ny = xx+origin[0]-source['nativeGlobalBox'][0],yy+origin[1]-source['nativeGlobalBox'][1]
        assert nx.min()>=0 and nx.max()<NATIVE and ny.min()>=0 and ny.max()<NATIVE
        with Image.open(source['path']) as im:
            original = np.array(im)
        assert np.array_equal(candidate[yy,xx],original[ny,nx]),source['stem']
        assert sha(source['path'])==source['sha256']
        assert sha(source['record'])==source['recordSha256']
        counts[str(source['sourceId'])]=len(xx)
        total+=len(xx)
    assert total==4096**2
    return {'pixelCount':total,'mismatchedPixels':0,'exactSameGlobalCoordinateSourcePixels':True,
            'sourceIdPixelCounts':counts,'sourceInputsAndRecordsUnchanged':True,
            'interpolation':False,'feathering':False,'colorAdjustment':False,'displacement':False}

def build_candidate(tile,prefix,check_only=False):
    """Inventory, assemble, write QA artifacts, then validate reopened art and mask."""
    if not re.fullmatch(r'c04-hardseam-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',prefix):
        raise ValueError('Output prefix must remain inside qa/c04-hardseam-*.')
    inventory = inspect_sources(tile)
    if inventory['missing'] or check_only:
        return {**inventory,'artworkWritten':False,
                'message':'Native sources are incomplete; fill the listed source slots and records, then rerun.' if inventory['missing'] else 'Source files are present; check-only has not assembled or written artwork.'}
    if list(QA.glob(prefix+'-*')):
        raise ValueError(f'QA prefix already exists: {prefix}. Choose a new version prefix.')
    arrays,inputs,origin = read_sources(inventory)
    candidate,ids,seams = assemble(arrays,origin)
    straight = np.concatenate([np.concatenate([arrays[r*4+c][HALO:HALO+STEP,HALO:HALO+STEP] for c in range(4)],1) for r in range(4)],0)
    outputs=[]
    def save(label,array,extra=None):
        path = QA/(prefix+'-'+label+'.png')
        Image.fromarray(array).save(path)
        rec={'path':path.as_posix(),'dimensions':[array.shape[1],array.shape[0]],'sha256':sha(path)}
        if extra:
            rec.update(extra)
        outputs.append(rec)
        return path
    artpath = save('candidate-4096',candidate)
    idpath = save('source-id-mask',ids,{'sourceIdRange':[1,16]})
    save('straight-4096',straight)
    preview = np.array(Image.fromarray(candidate).resize((1254,1254),Image.Resampling.LANCZOS))
    save('preview-1254-QA-only',preview,{'resampledQAPreviewOnly':True})
    for y in (1024,2048,3072):
        for x in (1024,2048,3072):
            box=[x-300,y-300,x+300,y+300]
            save(f'cross-{x}-{y}-straight-left-candidate-right-100pct',np.concatenate((straight[y-300:y+300,x-300:x+300],candidate[y-300:y+300,x-300:x+300]),1),{'sourceCrop':box,'scale':'1:1'})
    disk,disk_ids = np.array(Image.open(artpath)),np.array(Image.open(idpath))
    validation = validate_pixels(disk,disk_ids,inputs,origin)
    assert np.array_equal(candidate,disk) and np.array_equal(ids,disk_ids)
    validation['diskRoundtripExact']=True
    trace={'tile':tile,'candidateOriginGlobal':origin,'nativeAssemblyOriginGlobal':[origin[0]-HALO,origin[1]-HALO],
           'assemblyDimensions':[4326,4326],'assemblyCrop':[115,115,4211,4211],
           'sourceIdPixelFormula':'For tile-local pixel (x,y) with sourceId s: native source coordinate = (x + originGlobal.x - s.nativeGlobalBox.x0, y + originGlobal.y - s.nativeGlobalBox.y0).',
           'parameters':PARAMS,'step':STEP,'overlap':OVERLAP,'halo':HALO,
           'selectionOrder':'Each row left-to-right, then rows top-to-bottom; horizontal seams take priority at crossings.',
           'binarySelectionRule':'Choose B at positions >= path in each overlap; choose A before path. No blend.',
           'sources':inputs,'seams':seams,'sourceIdMask':outputs[1]}
    tracepath = QA/(prefix+'-trace.json')
    dump(tracepath,trace)
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile,
            'status':'QA native candidate; not production acceptance; cannot repair source geometry',
            'selectedBaseArrayOnly':True,'nativeSourceCount':16,
            'additionalCandidateArtifactExcluded':inventory['separateCandidateArtifact'],
            'selectedMapSha256':inventory['indexSha256'],'selectedArray':inventory['selectedArray'],
            'candidateGlobalBox':[origin[0],origin[1],origin[0]+4096,origin[1]+4096],
            'scriptPath':Path(__file__).as_posix(),'scriptSha256':sha(__file__),
            'inputs':inputs,'outputs':outputs,'trace':{'path':tracepath.as_posix(),'sha256':sha(tracepath)},
            'validation':validation,
            'limitations':['Base 16-source assembly excludes any separately indexed later local repair composites.',
                           'Source lighting and geometry disagreement can survive or become more visible at a hard cut.',
                           'All output remains QA-only; external and cross-tile edges are not validated here.']}
    reportpath=QA/(prefix+'-report.json')
    dump(reportpath,report)
    return {'tile':tile,'status':'candidate_written','candidate':outputs[0],'report':reportpath.as_posix(),
            'trace':tracepath.as_posix(),'validatedPixels':validation['pixelCount'],'mismatchedPixels':0,
            'selectedBaseArrayOnly':True,'nativeSourceCount':16,'additionalCandidateArtifactExcluded':bool(inventory['separateCandidateArtifact'])}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tile',required=True,help='One-based tile key in current-native-map.json, e.g. r09_c04')
    parser.add_argument('--prefix',required=True,help='Fresh qa/c04-hardseam-* output prefix')
    parser.add_argument('--check-only',action='store_true',help='Report source inventory only, without writing artifacts')
    args=parser.parse_args()
    try:
        result=build_candidate(args.tile,args.prefix,args.check_only)
        print(json.dumps(result,ensure_ascii=True))
        sys.exit(2 if result['status']=='waiting_for_sources' else 0)
    except (ValueError,AssertionError,FileNotFoundError,json.JSONDecodeError) as exc:
        print(json.dumps({'tile':args.tile,'status':'invalid_input','message':str(exc)},ensure_ascii=True))
        sys.exit(1)
