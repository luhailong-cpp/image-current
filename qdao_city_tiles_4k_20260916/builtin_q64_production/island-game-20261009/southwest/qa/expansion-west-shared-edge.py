from pathlib import Path
import sys,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import native_tile_candidate as n
tile,other,prefix=sys.argv[1:]
d=n.load(ROOT/'qa'/'expansion-west-worker-map.json');main=n.load(ROOT/'current-native-map.json')
left=Path(d['candidateArtifacts'][tile]['path'])
right=Path(main['candidateArtifacts'][other]['path'])
a=Image.open(left).convert('RGB');b=Image.open(right).convert('RGB')
out=Image.new('RGB',(400,4096));out.paste(a.crop((3896,0,4096,4096)),(0,0));out.paste(b.crop((0,0,200,4096)),(200,0))
records=[]
for i in range(4):
    lo=max(0,i*1024-100);hi=min(4096,(i+1)*1024+100)
    path=ROOT/'qa'/f'{prefix}-segment-{i+1}-native100.png'
    out.crop((0,lo,400,hi)).save(path);records.append({'path':path.as_posix(),'sha256':n.sha(path),'scale':'1:1','y':[lo,hi]})
n.dump(ROOT/'qa'/f'{prefix}-manifest.json',{'tiles':[tile,other],'sources':[{'path':p.as_posix(),'sha256':n.sha(p)} for p in (left,right)],'crops':records})
print(json.dumps(records))

