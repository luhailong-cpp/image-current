from pathlib import Path
from PIL import Image
import json,hashlib,datetime
root=Path(__file__).resolve().parents[2]
rows=[]
for d,last in [('E',12),('W',6)]:
 for f in range(1,last+1):
  p=root/'runtime'/'attack'/d/f'{f:02}.png';r=root/'records'/'attack'/d/f'{f:02}.json'
  rec=json.loads(r.read_text(encoding='utf-8')); im=Image.open(p); a=im.getchannel('A')
  h=hashlib.sha256(p.read_bytes()).hexdigest(); native=Image.open(rec['native']['path']);na=native.getchannel('A')
  rows.append(dict(file=p.relative_to(root).as_posix(),sha256=h,recordSHAValid=h==rec['sha256'],size=list(im.size),mode=im.mode,alphaExtrema=a.getextrema(),alpha16bbox=a.point(lambda v:255 if v>16 else 0).getbbox(),nativeAlpha16bbox=na.point(lambda v:255 if v>16 else 0).getbbox(),promptExists=(root/rec['prompt']).is_file(),receiptExists=(root/rec['evidence']['receipt']).is_file(),nativeSHAValid=hashlib.sha256(Path(rec['native']['path']).read_bytes()).hexdigest()==rec['native']['sha256']))
out=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='attack E01-12 and W01-06 only',count=len(rows),uniqueHashes=len({x['sha256'] for x in rows}),checksPassed=all(x['recordSHAValid'] and x['size']==[1024,1024] and x['mode']=='RGBA' and x['alphaExtrema']==(0,255) and x['promptExists'] and x['receiptExists'] and x['nativeSHAValid'] for x in rows),dynamicReview='pending parent playback review',clientIntegration='not tested',frames=rows)
(root/'records'/'attack'/'owned-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
