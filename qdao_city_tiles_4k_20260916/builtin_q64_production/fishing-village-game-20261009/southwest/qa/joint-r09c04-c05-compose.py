"""Join two 4326 native contexts, then optionally apply native cross-edge repairs.

Use --manifest with mode='join' first, then mode='repair' with its trace.
All boxes are half-open; joint-core coordinates have origin r09_c04 core.
Outputs are new QA files only. No native/export file is modified.
"""
import sys
sys.dont_write_bytecode = True

from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import re
import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
ZONE = QA.parent
HELPER = ZONE / "tools" / "seam_helpers.py"
WIDTH, HEIGHT, STRIDE, HALO, OVERLAP = 8422, 4326, 4096, 115, 230
LEFT_HASH = 'ba88b210f10b824910bfaf42d78f32b53dc1b100c7a3e7af91156118c3b55d92'
WORLD = [12173, 32653, 20595, 36979]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def check_ref(ref):
    path = Path(ref['path']).resolve()
    require(re.fullmatch('[0-9a-f]{64}', ref.get('sha256', '')) is not None, 'Explicit SHA256 required')
    require(path.is_file() and sha(path) == ref['sha256'], 'Input missing or SHA256 mismatch: '+str(path))
    return {'path': path.as_posix(), 'sha256': ref['sha256']}


def rgb(ref, size):
    with Image.open(ref['path']) as im:
        require(im.size == size and im.mode in ('RGB', 'RGBA'), 'Wrong native image size/mode')
        if im.mode == 'RGBA':
            require(im.getextrema()[3] == (255, 255), 'Non-opaque input')
        return np.asarray(im.convert('RGB')).copy()


class Writer:
    def __init__(self, prefix):
        require(re.fullmatch('joint-[a-z0-9_-]+', prefix) is not None, 'Invalid output prefix')
        require(not list(QA.glob(prefix+'-*')), 'Output prefix already used; select a fresh prefix')
        self.prefix = prefix

    def path(self, suffix):
        path = QA / (self.prefix+'-'+suffix)
        require(path.parent == QA and not path.exists(), 'Refusing output overwrite')
        return path

    def json(self, suffix, value):
        p = self.path(suffix)
        with p.open('x', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')
        return {'path': p.as_posix(), 'sha256': sha(p)}

    def png(self, suffix, pixels):
        p = self.path(suffix)
        with p.open('xb') as f:
            Image.fromarray(pixels).save(f, format='PNG')
        require(np.array_equal(np.asarray(Image.open(p)), pixels), 'PNG pixel identity failed')
        return {'path': p.as_posix(), 'sha256': sha(p), 'size': [pixels.shape[1], pixels.shape[0]]}

    def npy(self, suffix, pixels):
        p = self.path(suffix)
        with p.open('xb') as f:
            np.save(f, pixels, allow_pickle=False)
        require(np.array_equal(np.load(p, allow_pickle=False), pixels), 'NPY identity failed')
        return {'path': p.as_posix(), 'sha256': sha(p), 'shape': list(pixels.shape), 'dtype': str(pixels.dtype)}


def finish(writer, pixels, ids, trace):
    require(pixels.shape == (HEIGHT, WIDTH, 3) and ids.shape == (HEIGHT, WIDTH), 'Wrong joint dimensions')
    trace['context'] = {**writer.png('context-native.png', pixels), 'globalBox': WORLD}
    trace['sourceIds'] = writer.npy('source-ids.npy', ids)
    trace['tiles'] = []
    for tile, box, world in [('r09_c04', [115,115,4211,4211], [12288,32768,16384,36864]),
                             ('r09_c05', [4211,115,8307,4211], [16384,32768,20480,36864])]:
        l,t,r,b = box
        trace['tiles'].append({'tile': tile, **writer.png(tile+'-candidate-4096.png', pixels[t:b,l:r]),
                               'cropFromJointContext': box, 'globalCoreBox': world})
    trace['qa'] = []
    for part, top in enumerate((0,800,1600,2400,3196),1):
        box = [3866, top+115, 4556, top+1015]
        l,t,r,b=box
        ref=writer.png(f'shared-part{part:02d}-100pct.png',pixels[t:b,l:r])
        record={**ref,'source':trace['context'],'sourceBox':box,
                'globalBox':[v+WORLD[i%2] for i,v in enumerate(box)],'operation':'integer crop only',
                'noResize':True,'noFeather':True,'noDrawing':True}
        writer.json(f'shared-part{part:02d}-100pct.png.derivation.json',record)
        trace['qa'].append(record)
    trace.update({'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
                  'status':'joint_native_candidate_pending_visual_review','internalComplete4k':0,'formalAcceptedCount':0,
                  'noResize':True,'noFeather':True,'noColourCorrection':True,'noDrawing':True,
                  'exportsModified':False,'script':{'path':Path(__file__).as_posix(),'sha256':sha(__file__)},
                  'repairFunctionSource':{'path':(QA/'repair-compose.py').as_posix(),'sha256':sha(QA/'repair-compose.py')},
                  'seamHelper':{'path':HELPER.as_posix(),'sha256':sha(HELPER)}})
    result=writer.json('trace.json',trace)
    print(json.dumps({'context':trace['context'],'trace':result,'tiles':trace['tiles']}),flush=True)
    return result


def join(manifest, writer, manifest_ref, repair_tool, helper):
    left_ref,right_ref=check_ref(manifest['leftContext']),check_ref(manifest['rightContext'])
    require(left_ref['sha256']==LEFT_HASH,'Wrong stable left repaired context')
    require(manifest.get('rightContextFinalInternalQa') is True,'Right context has not been confirmed final for this join')
    inputs=[left_ref,right_ref]
    provenance=[check_ref(v) for v in manifest['provenance']]
    require(len(provenance)>=2,'Both source provenance traces required')
    context_hashes={read(v['path']).get('context',{}).get('sha256') for v in provenance}
    require(left_ref['sha256'] in context_hashes and right_ref['sha256'] in context_hashes,'Provenance does not identify both actual contexts')
    a,b=rgb(left_ref,(4326,4326)),rgb(right_ref,(4326,4326))
    seam=helper._minimum_vertical_seam(a[:,-230:],b[:,:230])
    require(len(seam)==4326 and np.all(np.abs(np.diff(seam))<=1),'Invalid shared seam')
    mask=(np.arange(230)[None,:]>=seam[:,None])
    overlap=np.where(mask[:,:,None],b[:,:230],a[:,-230:])
    pixels=np.concatenate([a[:,:4096],overlap,b[:,230:]],axis=1)
    ids=np.zeros((4326,8422),dtype=np.uint8)
    ids[:,4096:4326]=mask.astype(np.uint8);ids[:,4326:]=1
    require(np.array_equal(pixels[:,:4326][ids[:,:4326]==0],a[ids[:,:4326]==0]),'Left pixel provenance failed')
    require(np.array_equal(pixels[:,4096:][ids[:,4096:]==1],b[ids[:,4096:]==1]),'Right pixel provenance failed')
    overlap_mask=writer.png('overlap-source-mask-bw.png',mask.astype(np.uint8)*255)
    trace={'mode':'join','manifest':manifest_ref,'sources':[left_ref,right_ref],'provenance':provenance,
           'sourceIdLegend':{'0':'r09_c04 stable repaired context','1':'r09_c05 final internally repaired context'},
           'method':'native 230px overlap minimum RGB squared error with existing center/edge regularizer; hard source choice',
           'seam':{'overlapJointContextBox':[4096,0,4326,4326],'xByRowInOverlap':seam.tolist(),
                   'xByRowInJointContext':(seam+4096).tolist(),'xByWorldRow':(seam+16269).tolist(),
                   'worldYStart':32653,'rightChosenAtOrRight':True,'mask':overlap_mask},
           'validation':{'sourcePixelIdentity':True,'inputsUnchanged':True},'repairTargets':[]}
    for item in manifest.get('repairTargets',[]):
        name=item['id'];box=item['jointCoreBox'];require(re.fullmatch('[a-z0-9_-]+',name) is not None,'Invalid target id')
        require(len(box)==4 and all(type(v) is int for v in box),'Invalid target box')
        cb=[v+115 for v in box];l,t,r,bt=cb
        require(r-l==1254 and bt-t==1254 and 0<=l<r<=8422 and 0<=t<bt<=4326,'Invalid native repair source box')
        source=writer.png(name+'-source-native.png',pixels[t:bt,l:r])
        target={**item,'jointContextBox':cb,'globalBox':[box[0]+12288,box[1]+32768,box[2]+12288,box[3]+32768],
                'source':source,'role':'native 1254 repair source derived by integer crop only'}
        writer.json(name+'-source-native.png.derivation.json',target)
        trace['repairTargets'].append(target)
    for ref in inputs+provenance:require(sha(ref['path'])==ref['sha256'],'Input changed during assembly')
    return finish(writer,pixels,ids,trace)


def repair(manifest,writer,manifest_ref,repair_tool,helper):
    base_ref=check_ref(manifest['baseJointTrace']);base=read(base_ref['path'])
    context_ref=check_ref(base['context']);ids_ref=check_ref(base['sourceIds'])
    pixels=rgb(context_ref,(8422,4326));original=pixels.copy()
    ids=np.load(ids_ref['path'],allow_pickle=False).copy();require(ids.shape==(4326,8422),'Wrong base source mask')
    before_ids=ids.copy();inputs=[base_ref,context_ref,ids_ref];traces=[];native_repairs=[]
    legend=dict(base['sourceIdLegend'])
    for source_id,item in enumerate(manifest['repairs'],2):
        require(source_id<255 and str(source_id) not in legend,'Source ID already in base; use a fresh join base')
        name=item['id'];require(re.fullmatch('[a-z0-9_-]+',name) is not None,'Invalid repair id')
        sr,rr=check_ref(item['source']),check_ref(item['repair']);inputs.extend([sr,rr])
        generation=check_ref(item['generationRecord']);inputs.append(generation)
        require(read(generation['path']).get('sha256')==rr['sha256'],'Repair generation hash mismatch')
        cb=item['jointContextBox'];require(len(cb)==4 and all(type(v) is int for v in cb),'Invalid repair box')
        l,t,r,b=cb;require(r-l==1254 and b-t==1254 and 0<=l<r<=8422 and 0<=t<b<=4326,'Repair outside joint')
        submitted=rgb(sr,(1254,1254));require(np.array_equal(submitted,original[t:b,l:r]),'Submitted source is not exact base crop')
        new=rgb(rr,(1254,1254));old=pixels[t:b,l:r].copy()
        bounds=repair_tool.box(item['repairBounds'],'repairBounds');x1,y1,x2,y2=bounds;m=item['margin']
        require(0<=x1<x2<=1254 and 0<=y1<y2<=1254 and type(m) is int and m>0 and 2*m<min(x2-x1,y2-y1),'Invalid hard-mask bounds/margin')
        mask,paths=repair_tool.closed_mask(old,new,bounds,m,cb,helper._minimum_vertical_seam)
        selected=mask.astype(bool);after=np.where(selected[:,:,None],new,old)
        require(np.array_equal(after[selected],new[selected]) and np.array_equal(after[~selected],old[~selected]),'Repair identity failed')
        pixels[t:b,l:r]=after;ids[t:b,l:r][selected]=source_id
        native_repairs.append((source_id,cb,new))
        npy=writer.npy(name+'-source-mask.npy',mask);png=writer.png(name+'-source-mask-bw.png',mask*255)
        after_ref=writer.png(name+'-after-100pct.png',after)
        record={**item,'generationRecord':generation,'sourceId':source_id,'paths':paths,'sourceMask':{'npy':npy,'blackWhitePng':png},
                'maskLegend':{'0':'previous composite','1':'AI native repair'},'afterNativeQa':after_ref,
                'pixelIdentityPass':True,'changedPixelCount':int(selected.sum())}
        traces.append(writer.json(name+'-repair-trace.json',record));legend[str(source_id)]=rr
    unchanged=ids<2
    require(np.array_equal(pixels[unchanged],original[unchanged]) and np.array_equal(ids[unchanged],before_ids[unchanged]),'Unselected joint pixels changed')
    for source_id,cb,new in native_repairs:
        l,t,r,b=cb;selected=ids[t:b,l:r]==source_id
        require(int((ids==source_id).sum())==int(selected.sum()) and
                np.array_equal(pixels[t:b,l:r][selected],new[selected]),'Final repair source identity failed')
    for ref in inputs:require(sha(ref['path'])==ref['sha256'],'Input changed during repair')
    trace={'mode':'repair','manifest':manifest_ref,'baseJointTrace':base_ref,'sources':base['sources'],
           'sourceIdLegend':legend,'repairs':traces,'method':'Four minimum-error hard paths intersected, no blend',
           'validation':{'sourcePixelIdentity':True,'unselectedBasePixelsUnchanged':True,'inputsUnchanged':True}}
    return finish(writer,pixels,ids,trace)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',required=True,type=Path)
    args=parser.parse_args();manifest=read(args.manifest)
    require(manifest.get('schemaVersion')==1,'Wrong manifest schema')
    writer=Writer(manifest['outputPrefix']);repair_tool=module(QA/'repair-compose.py','joint_repair_functions')
    helper=module(repair_tool.HELPER,'joint_hard_seam_helper')
    manifest_ref={'path':args.manifest.resolve().as_posix(),'sha256':sha(args.manifest)}
    if manifest['mode']=='join':join(manifest,writer,manifest_ref,repair_tool,helper)
    elif manifest['mode']=='repair':repair(manifest,writer,manifest_ref,repair_tool,helper)
    else:raise ValueError('Mode must be join or repair')


if __name__=='__main__':
    main()
