from pathlib import Path
import json,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import native_tile_candidate as n
original_inspect=n.inspect_sources
n.inspect_sources=lambda tile:original_inspect(tile,ROOT/'qa'/'expansion-east-worker-map.json')
tile,prefix=sys.argv[1:3]
result=n.build_candidate(tile,prefix)
im=Image.open(result['candidate']['path'])
views=[]
for axis in ('v','h'):
    for seam in (1024,2048,3072):
        for segment in range(4):
            a,b=segment*1024,(segment+1)*1024
            box=[seam-200,a,seam+200,b] if axis=='v' else [a,seam-200,b,seam+200]
            path=ROOT/'qa'/f'{prefix}-native-{axis}{seam}-seg{segment+1}.png'
            im.crop(box).save(path)
            views.append({'path':path.as_posix(),'sha256':n.sha(path),'crop':box,'scale':'1:1'})
for y in (1024,2048,3072):
    for x in (1024,2048,3072):
        box=[x-300,y-300,x+300,y+300]
        path=ROOT/'qa'/f'{prefix}-native-junction-{x}-{y}.png'
        im.crop(box).save(path)
        views.append({'path':path.as_posix(),'sha256':n.sha(path),'crop':box,'scale':'1:1'})
manifest=ROOT/'qa'/f'{prefix}-native-QA-manifest.json'
n.dump(manifest,{'tile':tile,'candidate':result['candidate'],'views':views,'status':'awaiting visual review','allOuterTileEdgesPassed':False,'formalAccepted':False})
print(json.dumps({**result,'nativeViewManifest':manifest.as_posix()}))
