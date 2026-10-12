from pathlib import Path
import sys,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import native_tile_candidate as n
north,south,prefix=sys.argv[1:]
d=n.load(ROOT/'qa'/'expansion-west-worker-map.json');main=n.load(ROOT/'current-native-map.json')
def source(t):
    art=d.get('candidateArtifacts',{}).get(t) or main['candidateArtifacts'][t]
    return Path(art['path'])
paths=[source(north),source(south)]
a,b=[Image.open(p).convert('RGB') for p in paths]
out=Image.new('RGB',(4096,400));out.paste(a.crop((0,3896,4096,4096)),(0,0));out.paste(b.crop((0,0,4096,200)),(0,200))
records=[]
for i in range(4):
    lo=max(0,i*1024-100);hi=min(4096,(i+1)*1024+100)
    path=ROOT/'qa'/f'{prefix}-segment-{i+1}-native100.png'
    assert not path.exists()
    out.crop((lo,0,hi,400)).save(path)
    records.append({'path':path.as_posix(),'sha256':n.sha(path),'scale':'1:1','x':[lo,hi]})
n.dump(ROOT/'qa'/f'{prefix}-manifest.json',{'tiles':[north,south],'sources':[{'path':p.as_posix(),'sha256':n.sha(p)} for p in paths],'operation':'same-coordinate crop and concatenate only; no artwork mutation','crops':records})
print(json.dumps(records))
