from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
from export_review_runtime import edge_counts
B=Path(__file__).resolve().parents[1]
p=B/'staging/run-SW-12-v5.png'
with Image.open(p) as im:
    native=edge_counts(im)
    out=edge_counts(im.resize((1024,1024),Image.Resampling.LANCZOS))
    assert not any(native.values()) and not any(out.values()),(native,out)
    alpha=im.getchannel('A');w,h=im.size
    mx=max(alpha.crop(box).getextrema()[1] for box in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
for file in ['review-run-SW.json','review/review-run-SW.json']:
    r=json.loads((B/file).read_text(encoding='utf-8-sig'))
    r['reviewedAt']=datetime.now(timezone.utc).isoformat();r['explicitVersionList'][11]=5
    f=r['frames'][11];f.update(file='staging/run-SW-12-v5.png',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
        edgeOpaquePixels=native,exportEdgeOpaquePixels=out,maxEdgeAlpha=mx,
        generationRecord='staging/run-SW-12-v5.png.generation.json',request='requests/run-SW-12-v5.json',
        prompt='prompts/run-SW-12-v5.txt')
    f['actualObservation']+=' v5保留手脚与持物姿态，右墨灵与左笔穗均收进边界，原生和1024四边alpha>128均0。'
    r['rejectedThisPass']['run-SW-12-v2']='原生通过但1024右边2个alpha>128像素。'
    r['rejectedThisPass']['run-SW-12-v3']='1024左边1个alpha129像素，笔穗留白不足。'
    (B/file).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native':native,'export':out,'maxNativeEdgeAlpha':mx}))
