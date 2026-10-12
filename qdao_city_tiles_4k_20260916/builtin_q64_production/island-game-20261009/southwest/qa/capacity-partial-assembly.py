"""Mechanical capacity-gate QA: actual c03 v04 plus selected c04 native cores.

Writes only qa/capacity-* artifacts. Missing c04 cores remain transparent black.
No generation, interpolation, feathering, colour changes, or displacement is used
for the full-resolution assembly. The separately labelled preview is downsampled.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

QA=Path(__file__).resolve().parent
ROOT=QA.parent
ORIGIN=(8192,32768)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def dump(p,x):
    Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def asset(p,role):
    p=Path(p)
    return {'path':p.as_posix(),'sha256':sha(p),'role':role}

def main():
    index_path=ROOT/'current-native-map.json'
    ack_path=ROOT/'capacity-gate-ack.json'
    index,ack=load(index_path),load(ack_path)
    assert ack['generationHoldActive'] is True
    protected=[asset(index_path,'selected source index; read only'),asset(ack_path,'capacity gate acknowledgement; read only')]
    left_entry=index['candidateArtifacts']['r09_c03']
    left_path,left_record_path=Path(left_entry['path']),Path(left_entry['record'])
    left_record=load(left_record_path)
    assert left_record['globalBox']==[8192,32768,12288,36864]
    assert sha(left_path)==left_record['sha256']
    left_report_path=Path(left_record['assemblyReport'])
    left_report=load(left_report_path)
    left_mask_path=Path(left_record['sourceIdMask'])
    left=Image.open(left_path)
    assert left.mode=='RGB' and left.size==(4096,4096)
    left_array=np.array(left)
    assert np.array_equal(left_array,np.array(Image.open(left_record['sourceCandidate'])))
    left_ids=np.array(Image.open(left_mask_path))
    assert left_ids.shape==(4096,4096) and np.array_equal(np.unique(left_ids),np.arange(1,19))
    for item in left_report['outputs']:
        if Path(item['path'])==left_mask_path:
            assert sha(left_mask_path)==item['sha256']
    output=np.zeros((4096,8192,4),np.uint8)
    output[:,:4096,:3]=left_array
    output[:,:4096,3]=255
    ids=np.zeros((4096,8192),np.uint8)
    ids[:,:4096]=left_ids
    sources=[]
    for source in left_report['inputs']:
        sources.append({**source,'side':'left','tile':'r09_c03','operation':'Retain exact final v04 source selection; includes source IDs 17 and 18 local native repairs'})
    missing,core_placements=[],[]
    selected=index['r09_c04']
    assert len(selected)==4 and all(len(row)==4 for row in selected)
    for row in range(4):
        for col in range(4):
            stem=selected[row][col]
            x,y=4096+col*1024,row*1024
            core_box=[12288+col*1024,32768+row*1024,13312+col*1024,33792+row*1024]
            slot=f's{row+1:02}_{col+1:02}'
            if not stem:
                missing.append({'tile':'r09_c04','slot':slot,'globalBox':core_box,'assemblyBox':[x,y,x+1024,y+1024],
                                'reason':'No selected native source; RGBA zeros, alpha 0; not filled'})
                continue
            path=ROOT/'native'/(stem+'.png')
            record_path=Path(str(path)+'.generation.json')
            record=load(record_path)
            assert sha(path)==record['sha256']
            co=record['coordinates']
            assert co['coreGlobalBox']==core_box and co['coreCrop']==[115,115,1139,1139]
            assert co['nativeGlobalBox']==[core_box[0]-115,core_box[1]-115,core_box[2]+115,core_box[3]+115]
            im=Image.open(path)
            assert im.mode=='RGB' and im.size==(1254,1254)
            core=np.array(im)[115:1139,115:1139]
            output[y:y+1024,x:x+1024,:3]=core
            output[y:y+1024,x:x+1024,3]=255
            sid=19+row*4+col
            ids[y:y+1024,x:x+1024]=sid
            source={'sourceId':sid,'side':'right','tile':'r09_c04','stem':stem,'slot':slot,
                    'path':path.as_posix(),'sha256':sha(path),'record':record_path.as_posix(),
                    'recordSha256':sha(record_path),'nativeGlobalBox':co['nativeGlobalBox'],
                    'coreGlobalBox':core_box,'sourceCrop':[115,115,1139,1139],
                    'assemblyBox':[x,y,x+1024,y+1024],'operation':'Exact native core crop and paste'}
            sources.append(source)
            core_placements.append(source)
    assert len(core_placements)==13 and len(missing)==3
    expected_missing={'s03_04','s04_03','s04_04'}
    assert {m['slot'] for m in missing}==expected_missing
    coverage=output[:,:,3]
    assert np.array_equal(coverage>0,ids>0)
    assert np.count_nonzero(coverage)==29*1024**2
    assert np.all(output[coverage==0]==0)
    artifacts=[]
    def save(name,array,meta=None):
        path=QA/('capacity-'+name+'.png')
        Image.fromarray(array).save(path)
        rec={**asset(path,'QA artifact'),'dimensions':[array.shape[1],array.shape[0]],'mode':Image.open(path).mode}
        if meta:
            rec.update(meta)
        artifacts.append(rec)
        return path
    full_path=save('partial-8192x4096',output,{'nativePixels':True,'formalAsset':False,'globalBox':[8192,32768,16384,36864]})
    mask_path=save('source-id-mask-8192x4096',ids,{'sourceIdZero':'No source / transparent hole'})
    save('coverage-mask-8192x4096',coverage,{'values':{'0':'missing native core','255':'existing exact native pixels'}})
    preview=Image.fromarray(output).resize((2048,1024),Image.Resampling.BOX)
    save('preview-2048x1024-QA-only',np.array(preview),{'nativePixels':False,'formalAsset':False,
           'resampling':'Pillow BOX, 4:1 downsample; RGBA retained; only overview QA, not production pixels',
           'transparentBackgroundPreserved':True})
    edge=output[:,3796:4396]
    assert np.all(edge[:,:,3]==255)
    edge_path=save('shared-edge-600x4096',edge[:,:,:3],{'nativePixels':True,'sourceCrop':[3796,0,4396,4096],
          'globalBox':[11988,32768,12588,36864],'verticalJoinX':300,
          'left':'actual final c03 v04 last 300 columns','right':'c04 selected first-column cores first 300 columns',
          'horizontalRowCuts':[1024,2048,3072]})
    for row in range(4):
        save(f'shared-edge-section-{row+1}-600x1024',edge[row*1024:(row+1)*1024,:,:3],
             {'nativePixels':True,'sourceCrop':[0,row*1024,600,(row+1)*1024],
              'derivedFrom':asset(edge_path,'full shared-edge strip'),'globalBox':[11988,32768+row*1024,12588,33792+row*1024]})
    for y in (1024,2048,3072):
        save(f'shared-edge-cross-y{y}-600x400',edge[y-200:y+200,:,:3],
             {'nativePixels':True,'sourceCrop':[0,y-200,600,y+200],
              'derivedFrom':asset(edge_path,'full shared-edge strip'),'globalBox':[11988,32768+y-200,12588,32768+y+200]})
    # Independent reopening, full coverage check, and exact native source replay.
    disk=np.array(Image.open(full_path))
    disk_ids=np.array(Image.open(mask_path))
    assert np.array_equal(disk,output) and np.array_equal(disk_ids,ids)
    counts={}
    checked=0
    for source in sources:
        sy,sx=np.where(disk_ids==source['sourceId'])
        assert len(sx)>0
        nx=sx+ORIGIN[0]-source['nativeGlobalBox'][0]
        ny=sy+ORIGIN[1]-source['nativeGlobalBox'][1]
        with Image.open(source['path']) as im:
            arr=np.array(im)
        assert nx.min()>=0 and ny.min()>=0 and nx.max()<arr.shape[1] and ny.max()<arr.shape[0]
        assert np.array_equal(disk[sy,sx,:3],arr[ny,nx]),source['stem']
        assert np.all(disk[sy,sx,3]==255)
        assert sha(source['path'])==source['sha256'] and sha(source['record'])==source['recordSha256']
        counts[str(source['sourceId'])]=len(sx)
        checked+=len(sx)
    holes=disk_ids==0
    assert np.all(disk[holes]==0) and int(holes.sum())==3*1024**2
    assert checked==29*1024**2
    assert np.array_equal(disk[:,:4096,:3],left_array)
    assert np.array_equal(np.array(Image.open(edge_path)),disk[:,3796:4396,:3])
    # Audit saved reference links used by contributing source records, separately
    # from sources needed to reproduce this mechanical output.
    reference_entries={}
    for source in sources:
        rec=load(source['record'])
        for ref in rec.get('references',[])+rec.get('derivedFrom',[]):
            if isinstance(ref,dict) and ref.get('path'):
                key=ref['path']
                if key not in reference_entries:
                    rp=Path(key)
                    item={'path':rp.as_posix(),'role':ref.get('role'),'exists':rp.is_file(),'expectedSha256':ref.get('sha256')}
                    if rp.is_file():
                        item['actualSha256']=sha(rp)
                        item['hashMatches']=not ref.get('sha256') or item['actualSha256']==ref['sha256']
                    reference_entries[key]=item
    for p in protected:
        assert sha(p['path'])==p['sha256']
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),
      'status':'capacity gate mechanical partial QA only; incomplete right tile; not a final asset',
      'generationHoldObserved':True,'imageGenerationCalls':0,'newCoordinatesCreated':False,
      'operation':'Use actual c03 v04 pixels and its 18-source mask; paste c04 selected 13 native cores unchanged; leave 3 absent cores alpha 0',
      'assemblyDimensions':[8192,4096],'assemblyGlobalBox':[8192,32768,16384,36864],
      'actualLeftFinal':asset(left_path,'actual c03 v04; not base 16-source approximation'),
      'actualLeftFinalRecord':asset(left_record_path,'c03 v04 derivation'),
      'actualLeftAssemblyReport':asset(left_report_path,'c03 v04 detailed 18-source trace'),
      'actualLeftSourceMask':asset(left_mask_path,'actual c03 v04 per-pixel sources'),
      'protectedInputs':protected,'script':asset(__file__,'mechanical assembly and validation script'),
      'sources':sources,'missingCores':missing,'artifacts':artifacts,
      'sourceIdMapping':'IDs 1..18 preserve actual c03 v04 provenance; IDs 19..34 correspond to c04 row-major slots; 0 is missing. Missing IDs 30,33,34 have no pixels.',
      'pixelReplayFormula':'source pixel = (assembly x+8192-source.nativeGlobalBox.x0, assembly y+32768-source.nativeGlobalBox.y0)',
      'validation':{'opaquePixelsVerified':checked,'transparentPixelsVerified':int(holes.sum()),
          'totalPixelsVerified':checked+int(holes.sum()),'nativeSourceCount':len(sources),
          'mismatchedPixels':0,'sourceIdPixelCounts':counts,'sameGlobalCoordinateExact':True,
          'leftExactlyActualV04':True,'rightExactlySelectedNativeCores':True,'missingPixelsRGBAZero':True,
          'sharedEdgeExactlyAssemblyCrop':True,'inputsAndRecordsUnchanged':True,'indexAndAcknowledgementUnchanged':True,
          'fullResolutionInterpolation':False,'feathering':False,'colorAdjustment':False,'displacement':False},
      'coverage':{'c03':{'regularCoreCoverage':'16/16','actualFinalSources':18},
          'c04':{'regularCoreCoverage':'13/16','completeNativeOuterEdges':['north','west'],
            'eastCoveredTileLocalY':[0,2048],'eastMissingTileLocalY':[2048,4096],
            'southCoveredTileLocalX':[0,2048],'southMissingTileLocalX':[2048,4096]},
          'sharedC03C04Edge':'all four vertical sections have sources; geometric continuity requires visual QA'},
      'referenceAudit':{'mechanicalRequiredInputFilesMissing':[],
        'savedGenerationReferences':list(reference_entries.values()),
        'missingHistoricalReferences':[r for r in reference_entries.values() if not r['exists']],
        'mismatchedHistoricalReferences':[r for r in reference_entries.values() if r.get('hashMatches') is False],
        'currentGlobalConfigExists':(ROOT.parents[3]/'config/image-generation.json').is_file(),
        'note':'Historical reference availability is reported separately; no missing reference was recreated and no generation was requested.'},
      'limitations':['Transparent areas mean ungenerated cores, not water or playable space.',
         'The c04 core-only assembly intentionally retains all original internal and external joins for inspection.',
         'No capacity, walkability, navigation, collision, camera scale, or production acceptance is established.']}
    dump(QA/'capacity-partial-assembly-report.json',report)
    print(json.dumps({'artifact':full_path.as_posix(),'edge':edge_path.as_posix(),
       'opaquePixelsVerified':checked,'transparentPixelsVerified':int(holes.sum()),'mismatchedPixels':0,
       'missingCoreSlots':[m['slot'] for m in missing],
       'missingHistoricalReferenceCount':len(report['referenceAudit']['missingHistoricalReferences']),
       'mismatchedHistoricalReferenceCount':len(report['referenceAudit']['mismatchedHistoricalReferences'])}))

if __name__=='__main__':
    main()
