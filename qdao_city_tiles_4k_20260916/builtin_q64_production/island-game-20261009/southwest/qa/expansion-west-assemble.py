"""West-only native assembly and 1:1 QA crops; no source/map mutation outside worker map."""
from pathlib import Path
import sys,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import native_tile_candidate as n
INDEX=ROOT/'qa'/'expansion-west-worker-map.json'
def main(tile,version):
    assert tile in n.load(INDEX)['assignedTiles']
    prefix=f'c04-hardseam-west-{tile.replace("_","")}-{version}'
    original_inspect=n.inspect_sources
    n.inspect_sources=lambda t: original_inspect(t,INDEX)
    result=n.build_candidate(tile,prefix)
    if result['status']!='candidate_written':
        print(json.dumps(result));return
    report=n.load(result['report'])
    art=Image.open(result['candidate']['path']).convert('RGB')
    crops=[]
    def crop(label,box):
        path=ROOT/'qa'/f'{prefix}-{label}-native100.png'
        art.crop(box).save(path)
        crops.append({'path':path.as_posix(),'box':box,'sha256':n.sha(path),'scale':'1:1'})
    for seam in range(1,4):
        z=seam*1024
        for segment in range(4):
            lo=max(0,segment*1024-100);hi=min(4096,(segment+1)*1024+100)
            crop(f'vertical-{seam}-segment-{segment+1}',[z-200,lo,z+200,hi])
            crop(f'horizontal-{seam}-segment-{segment+1}',[lo,z-200,hi,z+200])
    for y in (1024,2048,3072):
        for x in (1024,2048,3072):crop(f'junction-{x}-{y}',[x-300,y-300,x+300,y+300])
    manifest=ROOT/'qa'/f'{prefix}-qa-manifest.json'
    n.dump(manifest,{'tile':tile,'assembly':result,'reviewPending':True,'crops':crops})
    d=n.load(INDEX)
    d['candidateArtifacts'][tile]={**result['candidate'],'sourceReport':result['report'],'record':result['report'],'sourceIdMask':report['outputs'][1],'qaManifest':manifest.as_posix(),'nativePixelsVerified':True,'internalTileSeamsPassed':False,'externalTileSeamsPassed':False,'formalAccepted':False}
    n.dump(INDEX,d)
    print(json.dumps({'result':result,'qaManifest':manifest.as_posix(),'preview':report['outputs'][3]['path']}))
if __name__=='__main__':main(*sys.argv[1:])

