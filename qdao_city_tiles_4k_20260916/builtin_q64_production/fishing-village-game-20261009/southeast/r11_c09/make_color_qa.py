from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;O=R/'processed/colorpass'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((O/'colorpass-report.json').read_text(encoding='utf-8-sig'))
for axis in ['horizontal','vertical']:
 items=[s for s in m['seams'] if s['axis']==axis]
 for j in range(0,12,4):
  cv=Image.new('RGB',(1024,1088),'#333333');d=ImageDraw.Draw(cv)
  for k,s in enumerate(items[j:j+4]):
   im=Image.open(s['afterStrip'])
   if axis=='horizontal':cv.paste(im,(k*256,32));d.text((k*256+4,4),s['a']+'-'+s['b'],fill='white')
   else:cv.paste(im,(0,k*272+16));d.text((4,k*272),s['a']+'-'+s['b'],fill='white')
  cv.save(O/f'contact-{axis}-{j//4+1}-native.png')
for group in range(3):
 cv=Image.new('RGB',(1536,532),'#333333');d=ImageDraw.Draw(cv)
 for i,it in enumerate(m['crossings'][group*3:group*3+3]):
  cv.paste(Image.open(it['file']),(i*512,20));d.text((i*512+3,3),Path(it['file']).stem,fill='white')
 cv.save(O/f'cross-contact-row{group+1}-native.png')
Image.open(m['candidate']['file']).crop((1421,1741,2675,2995)).save(O/'joint-region-after-color-native.png')
print(json.dumps({'candidateSha256':m['candidate']['sha256'],'seams':len(m['seams']),'crosses':len(m['crossings']),'beforeMean':float(np.mean([s['before']['robustSegmentMeanAbsRgb'] for s in m['seams']])),'afterMean':float(np.mean([s['after']['robustSegmentMeanAbsRgb'] for s in m['seams']]))}))

