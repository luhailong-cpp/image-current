"""Read-only native source QA; every write is confined to this helper directory.

Uses the production pipeline's pure min-error functions. This never selects,
ingests, generates, updates progress, or grants a visual PASS.
"""
from __future__ import annotations
import argparse, importlib.util, json, re, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
HELPER = Path(__file__).resolve().parent
TILE_DIR = HELPER.parent
ROOT = TILE_DIR.parent
TILE = 'r03_c05'
spec = importlib.util.spec_from_file_location('readonly_native_pipeline', ROOT/'pipeline.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
assert (p.CORE,p.HALO,p.PATCH,p.OVERLAP)==(1024,115,1254,230)

def json_write(path,value):
    path.resolve().relative_to(HELPER)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def save(out,name,arr,world_box,rotate=False):
    im=Image.fromarray(arr)
    if rotate: im=im.transpose(Image.Transpose.ROTATE_90)
    path=out/(name+'.png')
    path.resolve().relative_to(HELPER)
    im.save(path)
    with Image.open(path) as check:
        assert check.size==im.size and check.tobytes()==im.tobytes()
    return {'file':str(path),'sha256':p.sha(path),'pixels':list(im.size),
            'worldBox':world_box,'rotationCCW90':rotate,'nativePixelScale':1,
            'sourceResampled':False,'actuallyViewed':False,'visualVerdict':'pending'}

def load_source(tile,pid,override=None):
    path=Path(override).resolve() if override else p.selected(ROOT/tile,pid)
    if not path.is_file(): return None
    info=p.native_info(path,require_record=False)
    info.update(p.coords(tile,pid))
    info['sourceSelection']='explicit-in-memory-override' if override else 'pipeline-selected'
    info['generationRecordPresent']=bool(info.get('generationRecord'))
    with Image.open(path) as im: arr=np.array(im.convert('RGB'))
    return {'info':info,'array':arr}

def merge_labels(left,right,seam):
    choose=np.arange(230)[None,:]>=seam[:,None]
    joined=np.where(choose,right[:,:230],left[:,-230:])
    return np.concatenate((left[:,:-230],joined,right[:,230:]),axis=1)

def pair_artifacts(out,label,a,b,axis,external=False):
    aa,bb=a['array'],b['array']
    if axis=='y': aa,bb=aa.transpose(1,0,2),bb.transpose(1,0,2)
    joined,seam=p.append_native(aa,bb)
    labels=merge_labels(np.zeros(aa.shape[:2],dtype=np.uint8),np.ones(bb.shape[:2],dtype=np.uint8),seam)
    if axis=='y': joined,labels=joined.transpose(1,0,2),labels.T
    ac,bc=a['info']['coreWorldBox'],b['info']['coreWorldBox']
    if axis=='x':
        box=[979,115,1299,1139]; world=[bc[0]-160,ac[1],bc[0]+160,ac[3]]
        assert ac[2]==bc[0] and ac[1]==bc[1]
    else:
        box=[115,979,1139,1299]; world=[ac[0],bc[1]-160,ac[2],bc[1]+160]
        assert ac[3]==bc[1] and ac[0]==bc[0]
    x0,y0,x1,y1=box
    piece=joined[y0:y1,x0:x1]
    mask=labels[y0:y1,x0:x1]
    sources=[a['info'],b['info']]
    artifact=save(out,label,piece,world,axis=='x')
    artifact.update({'kind':'pairwise-minimum-error','axis':axis,'sources':sources,
        'sourceMap':save(out,label+'-source-index',mask*255,world,axis=='x'),
        'sourceMapValues':{'0':0,'255':1},'formalBoundaryDisplayY':160,
        'displaySides':{'top':'east/right source B' if axis=='x' else 'north/top source A',
                        'bottom':'west/left source A' if axis=='x' else 'south/bottom source B'},
        'seamPath':seam.tolist(),'seamPathCoordinates':'0-based across native 230px overlap; indexed by native y for x seam or native x for y seam',
        'note':'Pairwise uses the production DP and native 1254px extent. Horizontal seam paths can differ from the full-width assembled-tile DP.'})
    records=[artifact]
    if external:
        # Also show the fixed formal tile boundary. A movable min-error seam
        # must never conceal a disagreement at the actual world boundary.
        hard=np.concatenate((aa[:,:1139],bb[:,115:]),axis=1)
        hardlabels=np.concatenate((np.zeros((1254,1139),np.uint8),np.ones((1254,1139),np.uint8)),axis=1)
        if axis=='y': hard,hardlabels=hard.transpose(1,0,2),hardlabels.T
        record=save(out,label+'-formal-hard-boundary',hard[y0:y1,x0:x1],world,axis=='x')
        record.update({'kind':'fixed-world-formal-boundary','axis':axis,'sources':sources,
            'sourceMap':save(out,label+'-formal-source-index',hardlabels[y0:y1,x0:x1]*255,world,axis=='x'),
            'formalBoundaryDisplayY':160,'sourceMapValues':{'0':0,'255':1},'displaySides':artifact['displaySides']})
        records.append(record)
    return records

def full_artifacts(out,available):
    arrays={(int(k[1:3])-1,int(k[4:6])-1):v['array'] for k,v in available.items()}
    image,paths=p.assemble_arrays(arrays,'minimum-error')
    pixels=np.array(image)
    sources=[available[k]['info'] for k in p.patch_ids()]
    masks=[]; n=0
    for r in range(4):
        row=np.full((1254,1254),r*4,dtype=np.uint8)
        for c in range(1,4):
            row=merge_labels(row,np.full((1254,1254),r*4+c,dtype=np.uint8),np.asarray(paths[n]['overlapPath']))
            n+=1
        masks.append(row)
    mask=masks[0].T
    for r in range(1,4):
        mask=merge_labels(mask,masks[r].T,np.asarray(paths[n]['overlapPath']));n+=1
    mask=mask.T[115:4211,115:4211]
    world0=p.tile_box(TILE)
    # Prove every assembled RGB pixel equals its indexed source at the same world coordinate.
    for i,info in enumerate(sources):
        loc=np.argwhere(mask==i)
        yy=loc[:,0]+world0[1]-info['worldBoxWithHalo'][1]
        xx=loc[:,1]+world0[0]-info['worldBoxWithHalo'][0]
        assert np.array_equal(pixels[loc[:,0],loc[:,1]],available[info['patch']]['array'][yy,xx])
    records=[]
    for axis in ('x','y'):
        for pos in (1024,2048,3072):
            for segment in range(4):
                start=segment*1024
                box=[pos-160,start,pos+160,start+1024] if axis=='x' else [start,pos-160,start+1024,pos+160]
                x0,y0,x1,y1=box
                wb=[x0+world0[0],y0+world0[1],x1+world0[0],y1+world0[1]]
                label=f'assembled-internal-{axis}{pos}-segment{segment+1:02d}'
                rec=save(out,label,pixels[y0:y1,x0:x1],wb,axis=='x')
                rec.update({'kind':'full-production-assembly','tileCropBox':box,'sources':sources,'sourceMap':save(out,label+'-source-index',mask[y0:y1,x0:x1],wb,axis=='x'),'sourceMapValues':'0..15 index sources array','formalBoundaryDisplayY':160})
                records.append(rec)
    json_write(out/'full-assembly-seam-paths.json',{'sources':sources,'seamPaths':paths,'nativePixelEqualityVerified':True})
    return records

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--patch',choices=list(p.patch_ids()),help='Only pairs touching this patch; can be unselected when --source is supplied.')
    ap.add_argument('--source',type=Path,help='Explicit 1254px PNG for --patch. Never changes selected state.')
    ap.add_argument('--no-external',action='store_true')
    ap.add_argument('--pairwise-only',action='store_true',help='Do not additionally reproduce full-tile assembly when all 16 sources exist.')
    ap.add_argument('--run-name',help='New output directory under qa-audit-helper/runs; never overwritten.')
    args=ap.parse_args()
    if args.source and not args.patch: ap.error('--source requires --patch')
    run=args.run_name or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    if not re.fullmatch(r'[A-Za-z0-9_-]+',run): ap.error('Invalid --run-name')
    out=HELPER/'runs'/run
    out.resolve().relative_to(HELPER)
    out.mkdir(parents=True,exist_ok=False)
    state_files=[ROOT/tile/name for tile in (TILE,'r03_c04','r04_c05') for name in ('selection.json','pipeline-selection.json','progress.json','worker-progress.json') if (ROOT/tile/name).is_file()]
    before={str(x):p.sha(x) for x in state_files}
    cache={};missing=[];errors=[];records=[]
    def get(tile,pid):
        key=(tile,pid)
        if key not in cache:
            try: cache[key]=load_source(tile,pid,args.source if tile==TILE and pid==args.patch else None)
            except Exception as e:
                errors.append({'tile':tile,'patch':pid,'error':str(e)});cache[key]=None
        return cache[key]
    pairs=[]
    for r in range(1,5):
        for c in range(1,5):
            pid=f's{r:02d}_{c:02d}'
            if c<4: pairs.append((TILE,pid,TILE,f's{r:02d}_{c+1:02d}','x',False))
            if r<4: pairs.append((TILE,pid,TILE,f's{r+1:02d}_{c:02d}','y',False))
    if not args.no_external:
        for i in range(1,5):
            pairs.append(('r03_c04',f's{i:02d}_04',TILE,f's{i:02d}_01','x',True))
            pairs.append((TILE,f's04_{i:02d}','r04_c05',f's01_{i:02d}','y',True))
    for ta,pa,tb,pb,axis,external in pairs:
        if args.patch and not ((ta==TILE and pa==args.patch) or (tb==TILE and pb==args.patch)):continue
        label=f'{"external" if external else "pairwise-internal"}-{axis}-{ta}-{pa}-to-{tb}-{pb}'
        a,b=get(ta,pa),get(tb,pb)
        if a is None or b is None:
            missing.append({'pair':label,'reason':'source missing or rejected; no placeholder image','missing':[f'{t}/{pid}' for t,pid,v in [(ta,pa,a),(tb,pb,b)] if v is None]});continue
        records.extend(pair_artifacts(out,label,a,b,axis,external))
    available={pid:get(TILE,pid) for pid in p.patch_ids()}
    available={k:v for k,v in available.items() if v is not None}
    full=len(available)==16 and not args.patch and not args.pairwise_only
    if full: records.extend(full_artifacts(out,available))
    after={str(x):p.sha(x) if x.is_file() else None for x in state_files}
    manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':TILE,'selectedSourcesAvailable':len(available),'pipelineFile':str(ROOT/'pipeline.py'),'pipelineSha256':p.sha(ROOT/'pipeline.py'),'algorithm':'production pipeline.append_native / minimum_seam; full assembly additionally uses pipeline.assemble_arrays when all 16 exist','operation':'same-world original pixels only; no resize, interpolation, blur, blending, pixel synthesis or color correction','selectionOverride':{'patch':args.patch,'file':str(args.source.resolve())} if args.source else None,'fullAssemblyIncluded':full,'artifacts':records,'skipped':missing,'errors':errors,'stateHashesBefore':before,'stateHashesAfter':after,'stateHashesStableDuringRun':before==after,'note':'Concurrent production may legitimately update state while this helper reads it. This helper does not write source or state files. All image verdicts remain pending actual view_image inspection. Pairwise QA is not equivalent to final full-tile assembly near crossing seams.','actuallyViewed':False,'visualVerdict':'pending','formalAccepted':False}
    json_write(out/'manifest.json',manifest)
    print(json.dumps({'manifest':str(out/'manifest.json'),'artifacts':len(records),'skipped':len(missing),'errors':errors,'fullAssemblyIncluded':full,'visualVerdict':'pending'},ensure_ascii=False))
    return 2 if errors else 0

if __name__=='__main__':sys.exit(main())
