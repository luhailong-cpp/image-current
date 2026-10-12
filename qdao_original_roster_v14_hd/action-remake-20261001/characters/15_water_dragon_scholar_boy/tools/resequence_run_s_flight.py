from pathlib import Path
import json
b=Path(__file__).resolve().parents[1]
p=b/'audit/run-NS-selection.json'
d=json.loads(p.read_text(encoding='utf-8'))
for f in d['frames']:
 if f['direction']=='S' and f['source'].split('/')[-1] in ['run-S-06-v2.png','run-S-07-v2.png','run-S-08-v2.png']:
  n={'run-S-06-v2.png':8,'run-S-07-v2.png':6,'run-S-08-v2.png':7}[f['source'].split('/')[-1]]
  f['frame']=n
  f['event']='first_flight_apex' if n==6 else None
  f['review']['notes'].append('按实际脚底高度重新选序：S05/07v2/08v2/06v2构成05—08腾空上升、最高点、下降、落地准备；保留原文件名、SHA与逐图来源。')
d['frames'].sort(key=lambda f:(f['direction'],f['frame']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(d['frames']))

