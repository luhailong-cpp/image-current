"""Record source alpha-edge evidence before policy cleanup; no image mutation."""
import json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
rows=[]
for rp in sorted((ROOT/'records').glob('*/*.generation.json')):
    if len(rp.name)!=18 or not rp.name[:2].isdigit():continue
    r=json.loads(rp.read_text(encoding='utf-8-sig'))
    source=Path(r['derivedFrom']['path'])
    if not source.exists():continue
    im=Image.open(source);a=im.getchannel('A');w,h=im.size
    edges=[a.crop(b) for b in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]]
    maxima=[x.getextrema()[1] for x in edges]
    bbox=a.point(lambda p:255 if p>64 else 0).getbbox()
    rows.append({'file':r['file'],'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'nativeSize':[w,h],'edgeOrder':['top','bottom','left','right'],'edgeAlphaMax':maxima,'alphaAbove64BBox':bbox,'solidBorderAttention':max(maxima)>64})
report={'framesChecked':len(rows),'attention':[x['file'] for x in rows if x['solidBorderAttention']],'note':'Alpha>64 at native edge is a review flag, not an automatic cropping verdict. Low alpha edge noise is not meaningful subject clipping.','frames':rows}
(ROOT/'records'/'native-edge-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['framesChecked','attention']}))
