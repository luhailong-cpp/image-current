"""Merge existing, disjoint source-ID selections at exactly the same coordinates."""
import argparse, copy
import numpy as np
from PIL import Image
from native_multi_tile_repair import ROOT, QA, SIZE, read_base, safe_prefix, require, sha, validate_pixels
from production import dump, now

def read_prefix(prefix):
    safe_prefix(prefix)
    return read_base([QA/(prefix+s) for s in ['-candidate-4096.png','-source-id-mask.png','-report.json']])

def key(s):
    return (s['path'].replace('\\','/').lower(),s['sha256'],tuple(s['nativeGlobalBox']))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-prefix',required=True)
    ap.add_argument('--donor-prefix',required=True)
    ap.add_argument('--source',action='append',required=True)
    ap.add_argument('--prefix',required=True)
    a=ap.parse_args(); safe_prefix(a.prefix)
    require(not list(QA.glob(a.prefix+'-*')),'Output prefix already exists')
    b,d=read_prefix(a.base_prefix),read_prefix(a.donor_prefix)
    require(b['tile']==d['tile'] and b['box']==d['box'],'Branches must describe the same tile')
    bk={key(s):s for s in b['inputs']}; dk={key(s):s for s in d['inputs']}
    selected_ids=[s['sourceId'] for s in d['inputs'] if s['stem'] in a.source]
    require(selected_ids,'No requested donor source contributes to this tile')
    require(all(s['stem'] in a.source for k,s in dk.items() if k not in bk),'Donor contains unexpected exclusive source')
    selected=np.isin(d['ids'],selected_ids)
    base_exclusive=np.isin(b['ids'],[s['sourceId'] for k,s in bk.items() if k not in dk])
    require(not np.any(selected & base_exclusive),'Branches overlap; visual integration is required')
    untouched=~(selected|base_exclusive)
    require(np.array_equal(b['base'][untouched],d['base'][untouched]),'Common branch regions differ')
    inputs=copy.deepcopy(b['inputs']); lookup={key(s):s['sourceId'] for s in inputs}
    used=set(lookup.values()); lut=np.zeros(256,np.uint8)
    for source in d['inputs']:
        k=key(source)
        if k not in lookup:
            sid=next(i for i in range(1,256) if i not in used)
            item=copy.deepcopy(source);item['sourceId']=sid
            inputs.append(item);lookup[k]=sid;used.add(sid)
        lut[source['sourceId']]=lookup[k]
    art=b['base'].copy(); ids=b['ids'].copy()
    art[selected]=d['base'][selected]; ids[selected]=lut[d['ids'][selected]]
    require(np.array_equal(art[~selected],b['base'][~selected]),'Unexpected change outside donor selection')
    validation=validate_pixels(art,ids,inputs,b['box'])
    validation.update({'branchSelectionsDisjoint':True,'commonBranchPixelsExact':True,'unchangedOutsideDonorSelection':True,'donorSelectedPixels':int(selected.sum())})
    outputs=[]
    for suffix,arr in [('candidate-4096',art),('source-id-mask',ids),('donor-selection-mask',selected.astype(np.uint8)*255)]:
        p=QA/f'{a.prefix}-{suffix}.png'
        with p.open('xb') as handle: Image.fromarray(arr).save(handle,format='PNG')
        outputs.append({'path':p.as_posix(),'sha256':sha(p),'dimensions':[SIZE,SIZE]})
    with Image.open(outputs[0]['path']) as im: require(np.array_equal(np.array(im),art),'Artifact disk roundtrip mismatch')
    with Image.open(outputs[1]['path']) as im: require(np.array_equal(np.array(im),ids),'Mask disk roundtrip mismatch')
    validation['diskRoundtripExact']=True
    parents=[]
    for branch in [b,d]:
        require([sha(p) for p in branch['paths']]==branch['hashes'],'Parent artifact changed while merging')
        parents.append({'files':[{'path':p.as_posix(),'sha256':h} for p,h in zip(branch['paths'],branch['hashes'])]})
    report={'createdAtUtc':now(),'tile':b['tile'],'candidateGlobalBox':b['box'],'status':'native composite; connected visual QA pending','algorithm':'Copy only existing donor source-ID selections into unchanged base at identical global pixel coordinates; no new cut or selection boundary','inputs':inputs,'outputs':outputs,'validation':validation,'parents':parents,'donorStems':a.source,'basePrefix':a.base_prefix,'donorPrefix':a.donor_prefix,'script':{'path':str(ROOT/'native_merge_disjoint_branches.py'),'sha256':sha(__file__)},'formalAccepted':False}
    p=QA/f'{a.prefix}-report.json';dump(p,report)
    print({'prefix':a.prefix,'tile':b['tile'],'sourceCount':len(inputs),'validation':validation,'report':str(p)})

if __name__=='__main__':main()
